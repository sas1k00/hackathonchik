/*
 * Панель учителя: корневые пробелы класса, типичные ошибки, мини-группы, тепловая карта.
 * Демо-класс — это симулированные ученики, прогнанные через тот же движок диагностики.
 */
(function () {
  const T = window.Tamyr;
  const esc = s => T.esc(s);
  const title = id => T.TOPIC[id].title;

  const DEMO_NAMES = ['Айгерим С.', 'Нурлан Б.', 'Дана К.', 'Арман Т.', 'Алия М.', 'Ерлан Ж.', 'Мадина О.', 'Тимур А.',
    'Асель Н.', 'Данияр Е.', 'Камила Р.', 'Санжар У.', 'Жанель Д.', 'Алихан С.', 'Томирис Б.', 'Ильяс К.',
    'Амина Ж.', 'Бекзат М.', 'Сабина Т.', 'Азамат Л.', 'Карина В.', 'Нурсултан Г.', 'Аружан П.', 'Ержан И.'];
  // Типичные «корни» и их условная частота — только для генерации демо-класса
  const DEMO_ROOTS = [['frac', 5], ['neg', 3], ['expr', 3], ['pct', 3], ['pow', 2], ['fsu', 2], ['prop', 2], ['root', 1], ['ineq', 1], ['linf', 1]];

  let demoCache = null;
  function demoClass() {
    if (demoCache) return demoCache;
    const rand = T.rng(2026);
    const bag = [];
    DEMO_ROOTS.forEach(([id, w]) => { for (let i = 0; i < w; i++) bag.push(id); });
    demoCache = DEMO_NAMES.map((name, i) => {
      const k = rand() < 0.2 ? 0 : rand() < 0.7 ? 1 : 2;
      const roots = [];
      while (roots.length < k) { const r = bag[Math.floor(rand() * bag.length)]; if (!roots.includes(r)) roots.push(r); }
      const res = T.runSimulated(T.GOALS[0].start, roots, 1000 + i);
      const c = T.store.compact(name, 'full', res);
      c.demo = true;
      return c;
    });
    return demoCache;
  }

  let showDemo = true;

  function roster() {
    return (showDemo ? demoClass() : []).concat(T.store.imported()).map(c => Object.assign(T.store.expand(c), { demo: !!c.demo }));
  }

  function csv(rows) {
    const head = ['Ученик'].concat(T.TOPICS.map(t => t.title), ['Корневые пробелы', 'Вопросов']);
    const lines = [head].concat(rows.map(r => [r.name].concat(T.TOPICS.map(t => r.status[t.id]), [r.rootGaps.map(title).join('; '), r.asked])));
    return '﻿' + lines.map(l => l.map(v => `"${String(v).replace(/"/g, '""')}"`).join(';')).join('\n');
  }

  T.viewTeacher = function (app) {
    const rows = roster();
    const n = rows.length;
    const rootCount = {};
    const groups = {};
    rows.forEach(r => r.rootGaps.forEach(g => { rootCount[g] = (rootCount[g] || 0) + 1; (groups[g] = groups[g] || []).push(r.name); }));
    const rootsSorted = Object.entries(rootCount).sort((a, b) => b[1] - a[1]);
    const misCount = {};
    rows.forEach(r => r.misconceptions.forEach(m => { misCount[m.id] = (misCount[m.id] || 0) + 1; }));
    const misSorted = Object.entries(misCount).sort((a, b) => b[1] - a[1]).slice(0, 6);
    const avgAsked = n ? Math.round(rows.reduce((s, r) => s + r.asked, 0) / n) : 0;
    const clean = rows.filter(r => !r.rootGaps.length).length;
    const maxRoot = rootsSorted.length ? rootsSorted[0][1] : 1;

    app.innerHTML = `
      <section class="result-head">
        <div>
          <p class="eyebrow">Панель учителя</p>
          <h1>Класс: корни, а не оценки</h1>
          <p class="lead">Вместо «средний балл 62%» — какие именно базовые темы тянут класс вниз и кого с кем объединить на 15-минутный разбор.</p>
        </div>
        <div class="stats">
          <div><b>${n}</b><span>учеников</span></div>
          <div><b>${avgAsked}</b><span>вопросов в среднем</span></div>
          <div><b>${clean}</b><span>без пробелов</span></div>
        </div>
      </section>
      <section class="card toolbar">
        <label class="switch"><input type="checkbox" id="demo" ${showDemo ? 'checked' : ''}> Демо-класс <span class="chip small warn">симуляция: ${DEMO_NAMES.length} виртуальных учеников</span></label>
        <details><summary>Добавить ученика по коду</summary>
          <textarea id="code" rows="3" placeholder="Вставьте код TMR1… со страницы результата ученика"></textarea>
          <div class="row"><button class="btn small primary" id="add">Добавить</button><button class="btn small ghost" id="clear">Удалить добавленных</button><span id="msg" class="small"></span></div>
        </details>
        <button class="btn small" id="csv" ${n ? '' : 'disabled'}>Скачать CSV</button>
      </section>
      ${n ? `
      <section class="grid2">
        <div class="card">
          <h2>Корневые пробелы класса</h2>
          <ul class="bars">${rootsSorted.map(([id, c]) => `<li><span class="lbl">${esc(title(id))}</span><span class="bar"><i style="width:${(c / maxRoot) * 100}%"></i></span><span class="val">${c}</span></li>`).join('') || '<li class="muted">Пробелов не найдено</li>'}</ul>
        </div>
        <div class="card">
          <h2>Самые частые ошибки мышления</h2>
          <ul class="mis">${misSorted.map(([id, c]) => `<li><b>${esc(T.MISCONCEPTIONS[id].title)}</b> <span class="chip small">${c} уч.</span><span class="fix">${esc(T.MISCONCEPTIONS[id].fix)}</span></li>`).join('') || '<li class="muted">Нет данных</li>'}</ul>
        </div>
      </section>
      <section class="card">
        <h2>Мини-группы для разбора</h2>
        <div class="groups">${rootsSorted.map(([id]) => `<div class="group"><h3>${esc(title(id))} <span class="muted small">· ${groups[id].length} уч.</span></h3><p class="small">${groups[id].map(esc).join(', ')}</p><p class="tiny muted">${esc(T.TOPIC[id].rule)}</p></div>`).join('')}</div>
      </section>
      <section class="card">
        <h2>Тепловая карта</h2>
        <div class="heat-wrap"><table class="heat">
          <thead><tr><th>Ученик</th>${T.TOPICS.map(t => `<th title="${esc(t.title)}"><span>${esc(t.short)}</span></th>`).join('')}</tr></thead>
          <tbody>${rows.map(r => `<tr><td>${esc(r.name)}${r.demo ? '' : ' <span class="chip small">реальный</span>'}</td>${T.TOPICS.map(t => {
            const st = r.status[t.id]; const root = r.rootGaps.includes(t.id);
            return `<td class="c-${st}${root ? ' c-root' : ''}" title="${esc(t.title)}: ${esc((T.LEGEND.find(l => l[0] === (root ? 'root' : st)) || ['', st])[1])}"></td>`;
          }).join('')}</tr>`).join('')}</tbody>
        </table></div>
        ${T.legendHtml()}
      </section>` : '<section class="card"><p>Пока нет учеников. Включите демо-класс или добавьте код ученика.</p></section>'}
    `;

    app.querySelector('#demo').addEventListener('change', e => { showDemo = e.target.checked; T.viewTeacher(app); });
    app.querySelector('#add').addEventListener('click', () => {
      const msg = app.querySelector('#msg');
      try { T.store.addImported(T.store.decode(app.querySelector('#code').value)); T.viewTeacher(app); }
      catch (e) { msg.textContent = 'Не удалось прочитать код — скопируйте его целиком.'; msg.className = 'small bad-msg'; }
    });
    app.querySelector('#clear').addEventListener('click', () => { T.store.clearImported(); T.viewTeacher(app); });
    app.querySelector('#csv').addEventListener('click', () => {
      const blob = new Blob([csv(rows)], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'tamyr-class.csv'; a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
  };
})();
