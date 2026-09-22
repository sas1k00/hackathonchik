/*
 * Интерфейс ученика: главная → выбор цели → адаптивная диагностика → карта знаний → план и практика.
 */
(function () {
  const T = window.Tamyr;
  const app = document.getElementById('app');
  const S = T.STATUS;

  const state = { name: '', goal: 'full', diag: null, result: null, compact: null, practice: null };
  T.appState = state;

  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  T.esc = esc;
  const topicTitle = id => T.TOPIC[id].title;

  function legendHtml() {
    return '<ul class="legend">' + T.LEGEND.map(([k, v]) => `<li><span class="sw sw-${k}"></span>${v}</li>`).join('') + '</ul>';
  }
  T.legendHtml = legendHtml;

  /* ---------- Главная ---------- */
  function viewHome() {
    const past = T.store.sessions();
    app.innerHTML = `
      <section class="hero">
        <p class="eyebrow">Трек EduTech · подготовка к ЕНТ по математике</p>
        <h1>Ошибка в квадратных уравнениях.<br>Причина — в дробях.</h1>
        <p class="lead">Tamyr находит не просто тему, где ученик ошибается, а <b>корневой пробел</b>, из-за которого рушатся все следующие темы. Вглубь он спускается только там, где ученик ошибается: без пробелов хватает около 9 вопросов. Затем строит короткий план — от корня наверх.</p>
        <div class="cta">
          <a class="btn primary" href="#setup">Пройти диагностику</a>
          <a class="btn" href="#teacher">Панель учителя</a>
        </div>
      </section>
      <section class="how">
        <div class="step"><span>1</span><h3>Начинаем со сложного</h3><p>Первые вопросы — по целевой теме. Если ученик справляется, всё, на чём она держится, засчитывается без лишних вопросов.</p></div>
        <div class="step"><span>2</span><h3>Спускаемся к корню</h3><p>Ошибся — спускаемся по графу из ${T.TOPICS.length} тем к пререквизитам. Каждый неверный вариант ответа связан с типичной ошибкой мышления.</p></div>
        <div class="step"><span>3</span><h3>Чиним снизу вверх</h3><p>План начинается с корневого пробела: правило, пример, разбор <i>вашей</i> ошибки и проверка. Учитель видит корни всего класса.</p></div>
      </section>
      ${past.length ? `<section class="card"><h2>Прошлые диагностики на этом устройстве</h2><ul class="past">${past.slice(0, 5).map((c, i) => {
        const r = T.store.expand(c);
        return `<li><span>${esc(r.name)} · ${new Date(r.time).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span><span class="muted">${r.rootGaps.length ? 'Корни: ' + r.rootGaps.map(topicTitle).join(', ') : 'Пробелов не найдено'}</span><button class="link" data-past="${i}">Открыть</button></li>`;
      }).join('')}</ul></section>` : ''}
    `;
    app.querySelectorAll('[data-past]').forEach(b => b.addEventListener('click', () => {
      const c = T.store.sessions()[Number(b.dataset.past)];
      const r = T.store.expand(c);
      state.name = r.name; state.goal = r.goal; state.compact = c; state.diag = null;
      state.result = Object.assign(fullResultFromCompact(r), {});
      location.hash = '#result';
    }));
  }

  function fullResultFromCompact(r) {
    const gaps = T.TOPICS.filter(t => r.status[t.id] === S.GAP).map(t => t.id);
    const traces = gaps.filter(g => !r.rootGaps.includes(g)).map(g => ({ topic: g, roots: r.rootGaps.filter(x => T.ancestors(g).has(x)) })).filter(t => t.roots.length);
    const plan = T.TOPICS.filter(t => r.status[t.id] === S.GAP || r.status[t.id] === S.RISK).sort((a, b) => a.level - b.level).map(t => t.id);
    return { status: r.status, gaps, rootGaps: r.rootGaps, traces, misconceptions: r.misconceptions.map(m => ({ id: m.id, count: m.count, topics: [] })), plan, asked: r.asked, fullTestSize: T.TOPICS.reduce((n, t) => n + Math.min(3, T.questionsByTopic[t.id].length), 0) };
  }

  /* ---------- Выбор цели ---------- */
  function viewSetup() {
    app.innerHTML = `
      <section class="card narrow">
        <h1>Диагностика</h1>
        <p class="muted">От 8 до 30 вопросов — чем больше пробелов, тем глубже спускаемся. Калькулятор не нужен, черновик пригодится. Если не знаете ответ — нажмите «Не знаю»: угадывание делает карту менее точной.</p>
        <form id="setup-form">
          <label class="field"><span>Ваше имя</span><input id="name" required maxlength="40" autocomplete="given-name" value="${esc(state.name)}" placeholder="Например, Айгерим"></label>
          <fieldset class="goals"><legend>Что проверяем?</legend>
            ${T.GOALS.map(g => `<label class="goal"><input type="radio" name="goal" value="${g.id}" ${g.id === state.goal ? 'checked' : ''}><span><b>${g.title}</b><small>${g.desc}</small></span></label>`).join('')}
          </fieldset>
          <button class="btn primary" type="submit">Начать</button>
        </form>
      </section>`;
    app.querySelector('#setup-form').addEventListener('submit', e => {
      e.preventDefault();
      state.name = app.querySelector('#name').value.trim() || 'Ученик';
      state.goal = app.querySelector('input[name=goal]:checked').value;
      const goal = T.GOALS.find(g => g.id === state.goal);
      state.diag = new T.Diagnostic(goal.start);
      state.result = null;
      location.hash = '#quiz';
    });
  }

  /* ---------- Вопросы ---------- */
  function reasonText(r) {
    if (!r) return '';
    if (r.kind === 'goal') return 'Целевая тема';
    if (r.kind === 'prereq') return `Проверяем основу темы «${topicTitle(r.from)}»`;
    if (r.kind === 'mis') return `Ваш ответ в теме «${topicTitle(r.from)}» похож на ошибку из этой темы`;
    return '';
  }

  function viewQuiz() {
    const d = state.diag;
    if (!d) { location.hash = '#setup'; return; }
    const cur = d.next();
    if (!cur) return finishDiagnostic();
    const status = {};
    T.TOPICS.forEach(t => { status[t.id] = d.state[t.id].status; });
    app.innerHTML = `
      <section class="quiz">
        <div class="qcard card">
          <div class="qmeta"><span class="chip">${esc(topicTitle(cur.topic))}</span><span class="muted">Вопрос ${d.log.length + 1}</span></div>
          <p class="why">${esc(reasonText(cur.reason))}</p>
          <h2 class="qtext">${esc(cur.question.text)}</h2>
          <div class="options">
            ${cur.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="key">${'АБВГ'[i]}</span>${esc(o.t)}</button>`).join('')}
          </div>
          <button class="btn ghost" data-i="skip">Не знаю</button>
        </div>
        <aside class="card side">
          <h3>Карта заполняется</h3>
          <div id="mini-graph"></div>
          ${legendHtml()}
        </aside>
      </section>`;
    T.renderGraph(app.querySelector('#mini-graph'), status, { current: cur.topic });
    app.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => {
      d.answer(b.dataset.i === 'skip' ? null : Number(b.dataset.i));
      viewQuiz();
    }));
  }

  function finishDiagnostic() {
    if (state.diag.saved) { location.hash = '#result'; return; }
    state.diag.saved = true;
    state.result = state.diag.result();
    state.compact = T.store.compact(state.name, state.goal, state.result);
    T.store.saveSession(state.compact);
    location.hash = '#result';
  }

  /* ---------- Результат ---------- */
  function viewResult() {
    const r = state.result;
    if (!r) { location.hash = '#home'; return; }
    const inferred = T.TOPICS.filter(t => r.status[t.id] === S.INFERRED).length;
    const noGaps = !r.gaps.length;
    const risk = T.TOPICS.filter(t => r.status[t.id] === S.RISK).map(t => t.id);
    app.innerHTML = `
      <section class="result-head">
        <div>
          <p class="eyebrow">Карта знаний · ${esc(state.name)}</p>
          <h1>${noGaps ? 'Пробелов не найдено' : r.rootGaps.length === 1 ? 'Найден 1 корневой пробел' : `Найдено корневых пробелов: ${r.rootGaps.length}`}</h1>
          <p class="lead">${noGaps ? 'Все проверенные темы подтверждены. Можно переходить к задачам формата ЕНТ повышенной сложности.' :
            `Главное — начать с корня: ${r.rootGaps.map(id => `<b>${esc(topicTitle(id))}</b>`).join(', ')}. Пока он не закрыт, темы выше будут «сыпаться».`}</p>
        </div>
        <div class="stats">
          <div><b>${r.asked}</b><span>вопросов задано</span></div>
          <div><b>${inferred}</b><span>тем засчитано без вопросов</span></div>
          <div><b>${r.gaps.length}</b><span>тем с пробелами</span></div>
        </div>
      </section>
      <section class="grid2">
        <div class="card">
          <h2>Карта</h2>
          <div id="result-graph"></div>
          ${legendHtml()}
        </div>
        <div class="col">
          ${r.traces.length ? `<div class="card"><h2>Откуда растут ошибки</h2><ul class="traces">${r.traces.map(t => `<li><span class="bad">${esc(topicTitle(t.topic))}</span><span class="arrow">→ корень:</span><span class="root">${t.roots.map(x => esc(topicTitle(x))).join(', ')}</span></li>`).join('')}</ul></div>` : ''}
          ${r.misconceptions.length ? `<div class="card"><h2>Замеченные ошибки мышления</h2><ul class="mis">${r.misconceptions.slice(0, 5).map(m => {
            const mc = T.MISCONCEPTIONS[m.id];
            return `<li><b>${esc(mc.title)}</b>${m.count > 1 ? ` <span class="chip small">×${m.count}</span>` : ''}<span class="fix">${esc(mc.fix)}</span></li>`;
          }).join('')}</ul></div>` : ''}
          ${r.plan.length ? `<div class="card"><h2>План: снизу вверх</h2><ol class="plan">${r.plan.map((id, i) => {
            const unlocked = !T.TOPIC[id].prereq.some(p => r.status[p] === S.GAP || r.status[p] === S.RISK);
            return `<li class="${r.status[id]}"><span>${esc(topicTitle(id))}${risk.includes(id) ? ' <small class="muted">(проверить после корня)</small>' : ''}</span>${unlocked ? `<a class="btn small ${i === 0 ? 'primary' : ''}" href="#practice/${id}">Разобрать</a>` : '<span class="muted small">🔒 после предыдущих</span>'}</li>`;
          }).join('')}</ol></div>` : ''}
          <div class="card">
            <h2>Отправить учителю</h2>
            <p class="muted small">Код содержит только имя и статусы тем. Учитель вставит его в своей панели.</p>
            <textarea id="share" readonly rows="3">${esc(T.store.encode(state.compact))}</textarea>
            <button class="btn small" id="copy">Скопировать код</button>
          </div>
        </div>
      </section>`;
    T.renderGraph(app.querySelector('#result-graph'), r.status, { rootGaps: r.rootGaps, onClick: id => { if (r.plan.includes(id)) location.hash = '#practice/' + id; } });
    app.querySelector('#copy').addEventListener('click', async e => {
      const ta = app.querySelector('#share');
      try { await navigator.clipboard.writeText(ta.value); } catch (err) { ta.select(); document.execCommand('copy'); }
      e.target.textContent = 'Скопировано';
    });
  }

  /* ---------- Практика по теме ---------- */
  function viewPractice(topicId) {
    const r = state.result;
    if (!r || !T.TOPIC[topicId]) { location.hash = '#home'; return; }
    const t = T.TOPIC[topicId];
    if (!state.practice || state.practice.topic !== topicId) {
      const fresh = T.practiceQueue(topicId, state.diag ? state.diag.state[topicId].answers.map(a => a.qid) : []);
      state.practice = { topic: topicId, queue: fresh, i: 0, right: 0, stage: 'lesson', feedback: null };
    }
    const p = state.practice;
    const myMis = r.misconceptions.filter(m => T.MISCONCEPTIONS[m.id].home === topicId);
    const homeMis = Object.entries(T.MISCONCEPTIONS).filter(([, m]) => m.home === topicId).slice(0, 3);

    if (p.stage === 'lesson') {
      app.innerHTML = `
        <section class="card narrow lesson">
          <p class="eyebrow">Разбор темы</p>
          <h1>${esc(t.title)}</h1>
          <div class="rule"><h3>Правило</h3><p>${esc(t.rule)}</p></div>
          <div class="example"><h3>Пример</h3><p class="mono">${esc(t.example)}</p></div>
          <div class="traps"><h3>${myMis.length ? 'Ваши ошибки в этой теме' : 'Частые ловушки'}</h3><ul>
            ${(myMis.length ? myMis.map(m => [m.id, T.MISCONCEPTIONS[m.id]]) : homeMis).map(([, m]) => `<li><b>${esc(m.title)}.</b> ${esc(m.fix)}</li>`).join('')}
          </ul></div>
          <button class="btn primary" id="go">Проверить себя: 2 задачи</button>
          <a class="btn ghost" href="#result">К карте</a>
        </section>`;
      app.querySelector('#go').addEventListener('click', () => { p.stage = 'check'; p.opts = null; viewPractice(topicId); });
      return;
    }

    if (p.stage === 'check') {
      const q = p.queue[p.i % p.queue.length];
      p.opts = p.opts || T.shuffle(q.options, Math.random);
      app.innerHTML = `
        <section class="card narrow">
          <div class="qmeta"><span class="chip">${esc(t.title)}</span><span class="muted">Проверка ${p.right + 1} из 2</span></div>
          <h2 class="qtext">${esc(q.text)}</h2>
          <div class="options">${p.opts.map((o, i) => `<button class="opt" data-i="${i}" ${p.feedback ? 'disabled' : ''}><span class="key">${'АБВГ'[i]}</span>${esc(o.t)}</button>`).join('')}</div>
          <div id="fb"></div>
        </section>`;
      app.querySelectorAll('.opt').forEach(b => b.addEventListener('click', () => {
        const o = p.opts[Number(b.dataset.i)];
        const fb = app.querySelector('#fb');
        app.querySelectorAll('.opt').forEach(x => { x.disabled = true; });
        b.classList.add(o.ok ? 'is-ok' : 'is-bad');
        if (o.ok) {
          p.right++;
          fb.innerHTML = `<p class="ok-msg">Верно!</p><button class="btn primary" id="nx">${p.right >= 2 ? 'Завершить тему' : 'Следующая'}</button>`;
        } else {
          p.right = 0;
          const m = o.mis && T.MISCONCEPTIONS[o.mis];
          fb.innerHTML = `<p class="bad-msg">Неверно. Правильный ответ: <b>${esc(p.opts.find(x => x.ok).t)}</b>.</p>${m ? `<p class="small">${esc(m.title)}. ${esc(m.fix)}</p>` : ''}<button class="btn" id="nx">Ещё раз</button>`;
        }
        app.querySelector('#nx').addEventListener('click', () => {
          p.i++; p.opts = null;
          if (p.right >= 2) { p.stage = 'done'; completeTopic(topicId); }
          viewPractice(topicId);
        });
      }));
      return;
    }

    const next = state.result.plan.find(id => !T.TOPIC[id].prereq.some(x => state.result.status[x] === S.GAP || state.result.status[x] === S.RISK));
    app.innerHTML = `
      <section class="card narrow center">
        <p class="eyebrow">Тема закрыта</p>
        <h1>${esc(t.title)} ✓</h1>
        <p class="lead">Две задачи подряд решены верно. Карта обновлена.</p>
        ${next ? `<a class="btn primary" href="#practice/${next}">Следующая тема: ${esc(topicTitle(next))}</a>` : '<p>План выполнен — пройдите диагностику ещё раз, чтобы подтвердить результат.</p>'}
        <a class="btn ghost" href="#result">К карте</a>
      </section>`;
    state.practice = null;
  }

  function completeTopic(id) {
    const r = state.result;
    r.status[id] = S.MASTERED;
    r.gaps = r.gaps.filter(x => x !== id);
    r.rootGaps = r.rootGaps.filter(x => x !== id);
    // новые корни: пробелы, у которых больше нет пробелов снизу
    r.gaps.forEach(g => {
      if (!r.rootGaps.includes(g) && ![...T.ancestors(g)].some(a => r.status[a] === S.GAP)) r.rootGaps.push(g);
    });
    r.plan = r.plan.filter(x => x !== id);
    r.traces = r.gaps.filter(g => !r.rootGaps.includes(g)).map(g => ({ topic: g, roots: r.rootGaps.filter(x => T.ancestors(g).has(x)) })).filter(t => t.roots.length);
    state.compact = T.store.compact(state.name, state.goal, r);
    T.store.updateLatest(state.compact);
  }

  /* ---------- Демо для питча: симулированный ученик с пробелом в дробях ---------- */
  function demoResult() {
    state.name = 'Демо-ученик'; state.goal = 'quad'; state.diag = null;
    const rand = T.rng(11);
    const d = new T.Diagnostic(['quad'], { rand });
    const s = T.simulateStudent(['frac'], rand, { known: 1, unknown: 0, misRate: 1 });
    let cur; while ((cur = d.next())) d.answer(s.pick(cur));
    state.result = d.result();
    state.compact = T.store.compact(state.name, state.goal, state.result);
    history.replaceState(null, '', '#result');
    viewResult();
  }
  function demoQuiz() {
    state.name = 'Демо-ученик'; state.goal = 'quad'; state.result = null;
    const rand = T.rng(11);
    state.diag = new T.Diagnostic(['quad'], { rand });
    const s = T.simulateStudent(['frac'], rand, { known: 1, unknown: 0, misRate: 1 });
    for (let i = 0; i < 7; i++) state.diag.answer(s.pick(state.diag.next()));
    history.replaceState(null, '', '#quiz');
    viewQuiz();
  }

  /* ---------- Роутер ---------- */
  function route() {
    const h = location.hash.replace('#', '') || 'home';
    const [view, arg] = h.split('/');
    document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('active', a.dataset.nav === view || (view === 'quiz' && a.dataset.nav === 'setup')));
    window.scrollTo(0, 0);
    if (view === 'setup') viewSetup();
    else if (view === 'quiz') viewQuiz();
    else if (view === 'result') viewResult();
    else if (view === 'practice') viewPractice(arg);
    else if (view === 'teacher') T.viewTeacher(app);
    else if (view === 'demo') demoResult();
    else if (view === 'demo-quiz') demoQuiz();
    else viewHome();
  }
  // Клавиши 1–4 выбирают вариант ответа
  document.addEventListener('keydown', e => {
    const idx = { '1': 0, '2': 1, '3': 2, '4': 3 }[e.key];
    if (idx == null || e.target.matches('input, textarea')) return;
    const btn = app.querySelectorAll('.opt:not([disabled])')[idx];
    if (btn) btn.click();
  });
  window.addEventListener('hashchange', route);
  document.addEventListener('DOMContentLoaded', route);
})();
