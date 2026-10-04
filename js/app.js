/*
 * Интерфейс: лендинг → диагностика → «Сегодня» (план) → урок → практика с подсказками → повторения.
 */
(function () {
  const T = window.Tamyr;
  const L = T.learner;
  const app = document.getElementById('app');

  const ui = { name: '', goal: 'full', diag: null, lesson: null, session: null, banner: null, confirmReset: false };
  T.appState = ui;

  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const title = id => T.TOPIC[id].title;
  const known = id => Object.prototype.hasOwnProperty.call(T.TOPIC, id);
  const fmtDate = ts => new Date(ts).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
  const plural = (n, one, few, many) => (n % 10 === 1 && n % 100 !== 11 ? one : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? few : many);

  const STATUS = { unknown: 'Не проверялось', gap: 'Пробел', learning: 'Изучаю', inferred: 'Засчитано', mastered: 'Освоено', solid: 'Закреплено', risk: 'Под угрозой' };

  /* keys — какие статусы показать (панель учителя видит только статусы из кода ученика). */
  function legendHtml(keys) {
    return '<ul class="legend">' + T.LEGEND.filter(([k]) => !keys || keys.includes(k)).map(([k, v]) => `<li><span class="sw sw-${k}"></span>${v}</li>`).join('') + '</ul>';
  }
  T.esc = esc;
  T.legendHtml = legendHtml;
  /* Что можно сделать с темой прямо сейчас. */
  function actionFor(id) {
    const st = L.topic(id).st;
    if (st === 'gap') return { href: '#lesson/' + id, label: 'Урок' };
    if (st === 'learning') return { href: '#practice/' + id, label: 'Практика' };
    return { href: '#check/' + id, label: st === 'inferred' ? 'Подтвердить' : st === 'unknown' ? 'Проверить' : 'Повторить' };
  }

  /* ---------- Лендинг ---------- */
  function viewLanding() {
    app.innerHTML = `
      <section class="hero">
        <p class="eyebrow">Подготовка к ЕНТ · математика</p>
        <h1>Не «повтори всё».<br>А с чего начать именно тебе.</h1>
        <p class="lead">Tamyr находит тему, из-за которой сыплются остальные, объясняет её по шагам и возвращается к ней, пока она не закрепится. Каждый день — короткий план, собранный под твои ошибки.</p>
        <div class="cta">
          <a class="btn primary" href="#start">Найти мой корень</a>
          <a class="btn" href="#demo">Посмотреть на примере</a>
          <a class="btn ghost" href="#teacher">Панель учителя</a>
        </div>
      </section>
      <section class="how">
        <div class="step"><span>1</span><h3>Диагноз</h3><p>Начинаем со сложной темы и спускаемся вниз только там, где ты ошибаешься. Неверный ответ показывает, какая именно ошибка мышления за ним стоит.</p></div>
        <div class="step"><span>2</span><h3>Урок и практика</h3><p>Правило, разбор примера по шагам и задачи с подсказками. После ошибки — объяснение именно твоей ошибки, а не просто «неверно».</p></div>
        <div class="step"><span>3</span><h3>Закрепление</h3><p>Освоенная тема возвращается через день, потом через три, потом через девять. Знание остаётся до экзамена, а не до вечера.</p></div>
      </section>
      <p class="muted small">Прототип. Сейчас внутри ${T.TOPICS.length} тем алгебры 5–9 классов — основа для 7 из 18 разделов спецификации ЕНТ по математике. Прогресс хранится только на этом устройстве.</p>`;
  }

  /* ---------- Старт ---------- */
  function viewStart() {
    app.innerHTML = `
      <section class="card narrow">
        <h1>С чего начнём?</h1>
        <p class="muted">Диагностика — от нескольких вопросов до 35: чем больше пробелов, тем глубже спускаемся. Её можно остановить в любой момент — план построится по тому, что уже известно. Не знаешь ответ — жми «Не знаю»: угадывание портит карту.</p>
        ${L.exists() ? '<p class="note">Новая диагностика заменит текущий прогресс.</p>' : ''}
        <form id="start-form">
          <label class="field"><span>Имя</span><input id="name" required maxlength="40" autocomplete="given-name" value="${esc(ui.name || (L.exists() ? L.get().name : ''))}" placeholder="Например, Айгерим"></label>
          <fieldset class="goals"><legend>Что проверяем?</legend>
            ${T.GOALS.map(g => `<label class="goal"><input type="radio" name="goal" value="${g.id}" ${g.id === ui.goal ? 'checked' : ''}><span><b>${g.title}</b><small>${g.desc}</small></span></label>`).join('')}
            <label class="goal"><input type="radio" name="goal" value="none" ${ui.goal === 'none' ? 'checked' : ''}><span><b>Без диагностики</b><small>Начать с основ: каждая тема проверяется двумя задачами по ходу</small></span></label>
          </fieldset>
          <button class="btn primary" type="submit">Начать</button>
        </form>
      </section>`;
    app.querySelector('#start-form').addEventListener('submit', e => {
      e.preventDefault();
      ui.name = app.querySelector('#name').value.trim() || 'Ученик';
      ui.goal = app.querySelector('input[name=goal]:checked').value;
      if (ui.goal === 'none') {
        L.startBlank(ui.name);
        ui.banner = 'Начинаем с основ. Каждую тему сначала проверим двумя задачами: знаешь — идём выше, нет — разберём.';
        location.hash = '#home';
        return;
      }
      ui.diag = new T.Diagnostic(T.GOALS.find(g => g.id === ui.goal).start);
      location.hash = '#quiz';
    });
  }

  /* ---------- Диагностика ---------- */
  function reasonText(r) {
    if (!r) return '';
    if (r.kind === 'goal') return 'Целевая тема';
    if (r.kind === 'prereq') return `Проверяем основу темы «${title(r.from)}»`;
    if (r.kind === 'mis') return `Твой ответ в теме «${title(r.from)}» похож на ошибку из этой темы`;
    return '';
  }

  function viewQuiz() {
    const d = ui.diag;
    if (!d) { location.hash = '#start'; return; }
    const cur = d.next();
    if (!cur) return finishDiagnostic();
    const status = {};
    T.TOPICS.forEach(t => { status[t.id] = d.state[t.id].status; });
    app.innerHTML = `
      <section class="quiz">
        <div class="qcard card">
          <div class="qmeta"><span class="chip">${esc(title(cur.topic))}</span><span class="muted">Вопрос ${d.log.length + 1}</span></div>
          <p class="why">${esc(reasonText(cur.reason))}</p>
          <h2 class="qtext">${esc(cur.question.text)}</h2>
          <div class="options">
            ${cur.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="key">${'АБВГ'[i]}</span>${esc(o.t)}</button>`).join('')}
          </div>
          <div class="row">
            <button class="btn ghost" data-i="skip">Не знаю</button>
            ${d.log.length >= 6 ? '<button class="btn ghost" id="stop">Хватит, показать план</button>' : ''}
          </div>
        </div>
        <aside class="card side">
          <h3>Карта заполняется</h3>
          <div id="mini-graph"></div>
        </aside>
      </section>`;
    T.renderGraph(app.querySelector('#mini-graph'), status, { current: cur.topic });
    app.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => {
      d.answer(b.dataset.i === 'skip' ? null : Number(b.dataset.i));
      viewQuiz();
    }));
    const stop = app.querySelector('#stop');
    if (stop) stop.addEventListener('click', finishDiagnostic);
  }

  function finishDiagnostic() {
    const res = ui.diag.result();
    L.fromDiagnostic(ui.name, res);
    ui.diag = null;
    const q = `${res.asked} ${plural(res.asked, 'вопрос', 'вопроса', 'вопросов')}`;
    ui.banner = res.rootGaps.length
      ? `Диагностика готова: ${q}. ${res.rootGaps.length === 1 ? 'Корень' : 'Корни'} — <b>${res.rootGaps.map(id => esc(title(id))).join(', ')}</b>. Начинаем снизу: пока корень не закрыт, темы выше будут сыпаться.`
      : `Диагностика готова: ${q}, пробелов не найдено. Дальше подтверждаем темы, засчитанные без вопросов, и идём выше.`;
    location.hash = '#home';
  }

  /* ---------- Сегодня ---------- */
  function statsHtml() {
    const c = L.counts(), s = L.streakDays();
    return `<div class="stats">
      <div><b>${L.readiness()}%</b><span>готовность по базе алгебры</span></div>
      <div><b>${c.done}<small>/${T.TOPICS.length}</small></b><span>тем освоено</span></div>
      <div><b>${s}</b><span>${plural(s, 'день', 'дня', 'дней')} подряд</span></div>
    </div>`;
  }

  function viewHome() {
    const tasks = L.today(), roots = L.roots(), open = L.openTopics(), status = L.statusMap();
    const total = tasks.reduce((n, t) => n + t.min, 0);
    const risk = T.TOPICS.filter(t => status[t.id] === 'risk').length;
    let lead;
    if (tasks[0] && tasks[0].base) {
      lead = `Пробел найден в теме <b>${esc(title(tasks[0].base))}</b>, но сначала проверим её основу — <b>${esc(title(tasks[0].topic))}</b>: корень может быть глубже.`;
    } else if (roots.length) {
      const dep = T.descendants(roots[0]).size;
      lead = `Начинаем с корня: <b>${esc(title(roots[0]))}</b>.${dep ? ` На нём ${plural(dep, 'держится', 'держатся', 'держится')} ещё ${dep} ${plural(dep, 'тема', 'темы', 'тем')}.` : ''}`;
    } else if (tasks.length) lead = 'Пробелов в работе нет — проверяем следующую тему и идём выше.';
    else lead = 'На сегодня всё сделано.';
    const nextDue = L.nextDue();
    // для каждого корня — какие темы в работе на нём стоят
    const traces = roots.map(r => ({ root: r, above: open.filter(id => id !== r && T.ancestors(id).has(r)) })).filter(t => t.above.length);
    const PATH_MAX = 6;

    app.innerHTML = `
      <section class="result-head">
        <div>
          <p class="eyebrow">Сегодня · ${fmtDate(L.now())}</p>
          <h1>Привет, ${esc(L.get().name)}</h1>
          <p class="lead">${lead}</p>
        </div>
        ${statsHtml()}
      </section>
      ${ui.banner ? `<p class="banner">${ui.banner}</p>` : ''}
      <section class="grid2">
        <div class="card">
          <h2>План на сегодня ${tasks.length ? `<span class="muted small">≈ ${total} мин</span>` : ''}</h2>
          ${tasks.length ? `<ol class="tasks">${tasks.map((t, i) => `
            <li>
              <div><span class="chip small k-${t.kind}">${t.label}</span> <b>${esc(title(t.topic))}</b><span class="fix">${esc(t.why)} · ${t.min} мин</span></div>
              <a class="btn small ${i === 0 ? 'primary' : ''}" href="#${t.kind}/${t.topic}">${i === 0 ? 'Начать' : 'Открыть'}</a>
            </li>`).join('')}</ol>`
          : `<p class="muted">Все темы на сегодня закрыты. ${nextDue ? `Следующее повторение — ${fmtDate(nextDue)}.` : ''}</p><a class="btn small" href="#map">Открыть карту</a>`}
        </div>
        <div class="col">
          ${open.length ? `<div class="card"><h2>Твой путь: снизу вверх</h2><ol class="plan">${open.slice(0, PATH_MAX).map(id => {
            const a = actionFor(id), lock = L.locked(id);
            return `<li class="${L.topic(id).st}"><span>${esc(title(id))} <small class="muted">${STATUS[L.topic(id).st].toLowerCase()}</small></span>${lock ? '<span class="muted small">после предыдущих</span>' : `<a class="btn small" href="${a.href}">${a.label}</a>`}</li>`;
          }).join('')}</ol>
            ${open.length > PATH_MAX ? `<p class="muted small">И ещё ${open.length - PATH_MAX} ${plural(open.length - PATH_MAX, 'тема', 'темы', 'тем')} выше — они откроются по мере продвижения.</p>` : ''}
            ${risk ? `<p class="muted small">${risk} ${plural(risk, 'тема', 'темы', 'тем')} над пробелами ещё не ${plural(risk, 'проверялась', 'проверялись', 'проверялись')} — дойдём до них, когда основа будет готова.</p>` : ''}</div>` : ''}
          ${traces.length ? `<div class="card"><h2>Откуда растут ошибки</h2><ul class="traces">${traces.map(t => `<li><span class="root">${esc(title(t.root))}</span><span class="arrow">держит:</span><span>${t.above.map(x => esc(T.TOPIC[x].short)).join(', ')}</span></li>`).join('')}</ul></div>` : ''}
          <div class="card"><h2>Карта знаний</h2><div id="home-graph"></div><a class="btn small" href="#map">Открыть карту</a></div>
        </div>
      </section>`;
    ui.banner = null;
    T.renderGraph(app.querySelector('#home-graph'), status, { rootGaps: roots });
  }

  /* ---------- Урок ---------- */
  function viewLesson(id, fresh) {
    if (fresh || !ui.lesson || ui.lesson.topic !== id) ui.lesson = { topic: id, shown: 1 };
    const t = T.TOPIC[id], les = T.LESSONS[id], shown = ui.lesson.shown, done = shown >= les.steps.length;
    const above = [...T.descendants(id)].map(title);
    const mine = Object.keys(L.get().mis).filter(k => T.MISCONCEPTIONS[k].home === id).map(k => T.MISCONCEPTIONS[k]);
    const traps = mine.length ? mine : Object.values(T.MISCONCEPTIONS).filter(m => m.home === id).slice(0, 3);
    app.innerHTML = `
      <section class="card narrow lesson">
        <p class="eyebrow">Урок · шаг ${Math.min(shown, les.steps.length)} из ${les.steps.length}</p>
        <h1>${esc(t.title)}</h1>
        ${above.length ? `<p class="muted">Зачем: на этой теме ${plural(above.length, 'держится', 'держатся', 'держатся')} ${esc(above.slice(0, 4).join(', '))}${above.length > 4 ? ` и ещё ${above.length - 4}` : ''}.</p>` : ''}
        <div class="rule"><h3>Правило</h3><p>${esc(t.rule)}</p></div>
        <div class="worked">
          <h3>Разбор по шагам</h3>
          <p class="task">${esc(les.task)}</p>
          <ol class="steps">${les.steps.slice(0, shown).map(([say, math]) => `<li><span class="say">${esc(say)}</span><span class="mono">${esc(math)}</span></li>`).join('')}</ol>
          ${done ? `<p class="takeaway">${esc(les.takeaway)}</p>` : '<p class="muted small">Сначала подумай, что сделаешь дальше, — потом открой шаг.</p><button class="btn" id="more">Следующий шаг</button>'}
        </div>
        ${done ? `
          <div class="traps"><h3>${mine.length ? 'Твои ошибки в этой теме' : 'Частые ловушки'}</h3><ul>${traps.map(m => `<li><b>${esc(m.title)}.</b> ${esc(m.fix)}</li>`).join('')}</ul></div>
          <button class="btn primary" id="go">Теперь ты: практика</button>` : ''}
        <a class="btn ghost" href="#home">На главную</a>
      </section>`;
    const more = app.querySelector('#more');
    if (more) more.addEventListener('click', () => { ui.lesson.shown++; viewLesson(id); });
    const go = app.querySelector('#go');
    if (go) go.addEventListener('click', () => { L.completeLesson(id); location.hash = '#practice/' + id; });
  }

  /* ---------- Практика и проверка ---------- */
  function newQuestion(s) {
    s.q = T.nextQuestion(s.topic, L.topic(s.topic).seen);
    s.opts = T.shuffle(s.q.options, Math.random);
    s.hints = 0; s.answered = null; s.flagged = null;
  }

  function viewSession(mode, id) {
    if (!ui.session || ui.session.mode !== mode || ui.session.topic !== id || ui.session.done) {
      ui.session = { mode, topic: id, n: 0, right: 0, wrongRow: 0, mastered: false, done: false };
      newQuestion(ui.session);
    }
    renderSession();
  }

  function pips(n) {
    return `<span class="pips" title="Верных подряд без подсказок">${Array.from({ length: L.NEED }, (_, i) => `<i class="${i < n ? 'on' : ''}"></i>`).join('')}</span>`;
  }

  function renderSession() {
    const s = ui.session, t = T.TOPIC[s.topic], sol = T.solutionOf(s.q), a = s.answered;
    const practice = s.mode === 'practice';
    const progress = practice ? pips(s.mastered ? L.NEED : L.topic(s.topic).streak) : `<span class="muted">Вопрос ${Math.min(s.n + (a ? 0 : 1), L.CHECK_SIZE)} из ${L.CHECK_SIZE}</span>`;
    const hints = [];
    if (s.hints >= 1) hints.push(`<p><b>Правило.</b> ${esc(t.rule)}</p>`);
    if (s.hints >= 2 && sol.length) hints.push(`<p><b>Первый шаг.</b> ${esc(sol[0])}</p>`);
    if (s.hints >= 3 && sol.length > 1) hints.push(`<p><b>Дальше.</b></p><ol class="steps">${sol.slice(1).map(x => `<li><span class="mono">${esc(x)}</span></li>`).join('')}</ol>`);

    let feedback = '';
    if (a) {
      const m = a.opt && a.opt.mis ? T.MISCONCEPTIONS[a.opt.mis] : null;
      const last = practice ? s.mastered : s.n >= L.CHECK_SIZE;
      feedback = `<div class="feedback ${a.ok ? 'good' : 'bad'}">
        ${a.ok ? `<p class="ok-msg">Верно!${practice && s.hints >= 2 ? ' <span class="muted small">С подсказкой — в серию не идёт. Следующую попробуй без неё.</span>' : ''}</p>`
          : `<p class="bad-msg">${a.opt ? 'Неверно.' : 'Ничего страшного.'} Правильный ответ: <b>${esc(s.opts.find(o => o.ok).t)}</b>.</p>`}
        ${m ? `<p><b>Похоже на типичную ошибку:</b> ${esc(m.title[0].toLowerCase() + m.title.slice(1))}. ${esc(m.fix)}</p>` : ''}
        ${s.flagged ? `<p class="note">Эта ошибка родом из темы «${esc(title(s.flagged))}» — она поставлена на проверку сегодня.</p>` : ''}
        ${sol.length ? `<h3>Разбор</h3><ol class="steps">${sol.map(x => `<li><span class="mono">${esc(x)}</span></li>`).join('')}</ol>` : ''}
        <div class="row">
          <button class="btn primary" id="next">${last ? (practice ? 'Завершить тему' : 'Итог') : (practice ? 'Следующая задача' : 'Следующий вопрос')}</button>
          ${practice && s.wrongRow >= 2 ? `<a class="btn" href="#lesson/${s.topic}">Вернуться к уроку</a>` : ''}
        </div>
      </div>`;
    }

    app.innerHTML = `
      <section class="card narrow session">
        <div class="qmeta"><span class="chip">${esc(t.title)}</span>${progress}</div>
        <p class="why">${practice ? `Практика: ${L.NEED} верных подряд без подсказок — и тема освоена` : 'Проверка без подсказок: два вопроса'}</p>
        <h2 class="qtext">${esc(s.q.text)}</h2>
        <div class="options">${s.opts.map((o, i) => `<button class="opt ${a && o.ok ? 'is-ok' : ''} ${a && a.idx === i && !o.ok ? 'is-bad' : ''}" data-i="${i}" ${a ? 'disabled' : ''}><span class="key">${'АБВГ'[i]}</span>${esc(o.t)}</button>`).join('')}</div>
        ${a ? '' : `<div class="row">
          ${practice ? `<button class="btn small" id="hint" ${s.hints >= 3 ? 'disabled' : ''}>${['Подсказка', 'Ещё подсказка', 'Показать решение', 'Подсказки кончились'][s.hints]}</button>` : ''}
          <button class="btn ghost small" id="skip">Не знаю</button>
        </div>`}
        ${hints.length && !a ? `<div class="hintbox">${hints.join('')}</div>` : ''}
        ${feedback}
        <a class="btn ghost small" href="#home">На главную</a>
      </section>`;

    const answer = idx => {
      const opt = idx === null ? null : s.opts[idx];
      const ok = !!(opt && opt.ok);
      s.answered = { idx, ok, opt };
      s.n++;
      if (ok) s.right++;
      s.flagged = L.recordAnswer(s.topic, s.q, ok ? null : opt);
      if (practice) {
        s.mastered = L.practiceAnswer(s.topic, ok, s.hints < 2);
        s.wrongRow = ok ? 0 : s.wrongRow + 1;
      }
      renderSession();
    };
    if (!a) {
      app.querySelectorAll('.opt').forEach(b => b.addEventListener('click', () => answer(Number(b.dataset.i))));
      app.querySelector('#skip').addEventListener('click', () => answer(null));
      const hint = app.querySelector('#hint');
      if (hint) hint.addEventListener('click', () => { s.hints++; renderSession(); });
    } else {
      app.querySelector('#next').addEventListener('click', () => {
        if (practice ? s.mastered : s.n >= L.CHECK_SIZE) return finishSession();
        newQuestion(s);
        renderSession();
      });
    }
  }

  function finishSession() {
    const s = ui.session, id = s.topic;
    s.done = true;
    let head, text;
    if (s.mode === 'practice') {
      head = 'Тема освоена ✓';
      text = `${L.NEED} задачи подряд без подсказок. Тема вернётся на повторение завтра — так она останется в памяти до экзамена.`;
    } else {
      const pass = L.checkResult(id, s.right), x = L.topic(id);
      head = pass ? (x.st === 'solid' ? 'Закреплено ✓' : 'Подтверждено ✓') : 'Тема вернулась в работу';
      text = pass ? `Оба ответа верны. Следующее повторение через ${x.ivl} ${plural(x.ivl, 'день', 'дня', 'дней')} — ${fmtDate(x.due)}.`
        : `Верно ${s.right} из ${L.CHECK_SIZE}. Это нормально: лучше узнать сейчас, чем на экзамене. Тема добавлена в план.`;
    }
    const next = L.today()[0];
    app.innerHTML = `
      <section class="card narrow center">
        <p class="eyebrow">${esc(title(id))}</p>
        <h1>${head}</h1>
        <p class="lead">${text}</p>
        ${next ? `<a class="btn primary" href="#${next.kind}/${next.topic}">Дальше: ${esc(next.label.toLowerCase())} · ${esc(title(next.topic))}</a>` : '<p>На сегодня план выполнен.</p>'}
        <a class="btn ghost" href="#home">На главную</a>
      </section>`;
  }

  /* ---------- Карта ---------- */
  function viewMap() {
    const status = L.statusMap();
    const due = new Set(T.TOPICS.filter(t => L.isDue(t.id)).map(t => t.id));
    app.innerHTML = `
      <section class="card">
        <h1>Карта знаний</h1>
        <p class="muted">Основа внизу, сложные темы наверху. Нажми на тему, чтобы открыть урок, практику или проверку.</p>
        <div id="map-graph"></div>
        ${legendHtml()}
      </section>`;
    T.renderGraph(app.querySelector('#map-graph'), status, { rootGaps: L.roots(), due, onClick: id => { location.hash = actionFor(id).href; } });
  }

  /* ---------- Прогресс ---------- */
  /* Код «ученик → учитель» в формате Tamyr: панель учителя знает только статусы диагностики,
     поэтому «изучаю» передаём как пробел, «закреплено» — как освоено. */
  function shareCode() {
    const S = L.get(), map = L.statusMap(), status = {};
    T.TOPICS.forEach(t => { status[t.id] = { learning: 'gap', solid: 'mastered' }[map[t.id]] || map[t.id]; });
    const misconceptions = Object.entries(S.mis).map(([id, count]) => ({ id, count }));
    return T.store.encode(T.store.compact(S.name, 'full', { status, rootGaps: L.roots(), misconceptions, asked: S.diag ? S.diag.asked : 0 }));
  }
  function viewProgress() {
    const S = L.get();
    const mis = Object.entries(S.mis).sort((a, b) => b[1] - a[1]).slice(0, 5);
    const log = S.log.slice(-12).reverse();
    app.innerHTML = `
      <section class="result-head">
        <div><p class="eyebrow">Прогресс</p><h1>${esc(S.name)}</h1>
          <p class="lead">${S.diag ? `Диагностика ${fmtDate(S.diag.at)}: ${S.diag.asked} ${plural(S.diag.asked, 'вопрос', 'вопроса', 'вопросов')}, корней найдено: ${S.diag.roots.length}.` : 'Без входной диагностики: темы проверяются по ходу.'}</p></div>
        ${statsHtml()}
      </section>
      <section class="grid2">
        <div class="card">
          <h2>Твои типичные ошибки</h2>
          ${mis.length ? `<ul class="mis">${mis.map(([id, n]) => { const m = T.MISCONCEPTIONS[id]; return `<li><b>${esc(m.title)}</b>${n > 1 ? ` <span class="chip small">×${n}</span>` : ''}<span class="fix">${esc(m.fix)} · тема «${esc(title(m.home))}»</span></li>`; }).join('')}</ul>` : '<p class="muted">Пока не замечено ни одной типичной ошибки.</p>'}
        </div>
        <div class="col">
          <div class="card">
            <h2>История</h2>
            ${log.length ? `<ul class="log">${log.map(e => `<li class="e-${e.kind}"><span class="muted small">${fmtDate(e.t)}</span><span><b>${esc(title(e.topic))}</b> — ${esc(e.text.toLowerCase())}</span></li>`).join('')}</ul>` : '<p class="muted">Здесь появятся пройденные уроки и освоенные темы.</p>'}
          </div>
          <div class="card">
            <h2>Отправить учителю</h2>
            <p class="muted small">Код содержит только имя и текущие статусы тем. Учитель вставит его в своей панели и увидит карту класса.</p>
            <textarea id="share" readonly rows="3">${esc(shareCode())}</textarea>
            <button class="btn small" id="copy">Скопировать код</button>
          </div>
          <div class="card">
            <h2>Управление</h2>
            <p class="muted small">Перемотка нужна, чтобы показать интервальные повторения, не дожидаясь завтра. Сейчас в приложении ${fmtDate(L.now())}.</p>
            <div class="row">
              <button class="btn small" id="adv1">Демо: +1 день</button>
              <button class="btn small" id="adv3">+3 дня</button>
              <a class="btn small" href="#start">Диагностика заново</a>
              <button class="btn small danger" id="reset">${ui.confirmReset ? 'Точно сбросить?' : 'Сбросить прогресс'}</button>
            </div>
          </div>
        </div>
      </section>`;
    app.querySelector('#copy').addEventListener('click', async e => {
      const ta = app.querySelector('#share');
      try { await navigator.clipboard.writeText(ta.value); } catch (err) { ta.select(); document.execCommand('copy'); }
      e.target.textContent = 'Скопировано';
    });
    app.querySelector('#adv1').addEventListener('click', () => { L.advance(1); location.hash = '#home'; });
    app.querySelector('#adv3').addEventListener('click', () => { L.advance(3); location.hash = '#home'; });
    app.querySelector('#reset').addEventListener('click', () => {
      if (!ui.confirmReset) { ui.confirmReset = true; return viewProgress(); }
      ui.confirmReset = false; L.reset(); location.hash = '#home';
    });
  }

  /* ---------- Демо: ученица с корневым пробелом в дробях ---------- */
  function demo() {
    const rand = T.rng(11);
    const d = new T.Diagnostic(T.GOALS[0].start, { rand });
    const s = T.simulateStudent(['frac'], rand, { known: 1, unknown: 0, misRate: 1 });
    let cur; while ((cur = d.next())) d.answer(s.pick(cur));
    const res = d.result();
    L.fromDiagnostic('Айгерим', res);
    ui.banner = `Это демо: виртуальная ученица с пробелом в дробях прошла диагностику за ${res.asked} ${plural(res.asked, 'вопрос', 'вопроса', 'вопросов')}. Пройди её план или <a href="#start">начни свою диагностику</a>.`;
    history.replaceState(null, '', '#home');
    route();
  }

  /* ---------- Роутер ---------- */
  function route() {
    const h = location.hash.replace('#', '') || 'home';
    const [view, arg] = h.split('/');
    const group = { lesson: 'home', practice: 'home', check: 'home', start: 'home', quiz: 'home' }[view] || view;
    document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('active', a.dataset.nav === group));
    if (view !== 'progress') ui.confirmReset = false;
    window.scrollTo(0, 0);
    if (view === 'demo') return demo();
    if (view === 'start' || view === 'setup') return viewStart(); // #setup — адрес из хакатонной версии
    if (view === 'quiz') return viewQuiz();
    if (view === 'teacher') return T.viewTeacher(app);
    if (!L.exists()) return viewLanding();
    if (view === 'lesson' && known(arg)) return viewLesson(arg, true);
    if ((view === 'practice' || view === 'check') && known(arg)) return viewSession(view, arg);
    if (view === 'map') return viewMap();
    if (view === 'progress') return viewProgress();
    viewHome();
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
