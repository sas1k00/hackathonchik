/*
 * Хранение результатов на устройстве и обмен кодом «ученик → учитель» без сервера.
 */
(function () {
  const T = window.Tamyr;
  const KEY = 'tamyr.v1.sessions';
  const KEY_IMPORTED = 'tamyr.v1.imported';
  const CODE = { mastered: 'm', inferred: 'i', gap: 'g', risk: 'r', unknown: 'u' };
  const DECODE = Object.fromEntries(Object.entries(CODE).map(([k, v]) => [v, k]));

  function read(key) {
    try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch (e) { return []; }
  }
  function write(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* приватный режим — работаем без сохранения */ }
  }

  T.store = {
    compact(name, goal, res) {
      const s = T.TOPICS.map(t => CODE[res.status[t.id]] || 'u').join('');
      return { v: 1, n: name, g: goal, t: Date.now(), s, r: res.rootGaps, m: res.misconceptions.map(m => [m.id, m.count]), a: res.asked };
    },
    expand(c) {
      const status = {};
      T.TOPICS.forEach((t, i) => { status[t.id] = DECODE[c.s[i]] || 'unknown'; });
      return { name: c.n, goal: c.g, time: c.t, status, rootGaps: c.r || [], misconceptions: (c.m || []).map(([id, count]) => ({ id, count })), asked: c.a || 0 };
    },
    saveSession(c) { const all = read(KEY); all.unshift(c); write(KEY, all.slice(0, 30)); },
    updateLatest(c) { const all = read(KEY); if (all.length) { all[0] = c; write(KEY, all); } },
    sessions() { return read(KEY).map(c => T.store.sanitize(c)).filter(Boolean); },
    encode(c) { return 'TMR1.' + btoa(unescape(encodeURIComponent(JSON.stringify(c)))); },
    decode(code) {
      const raw = String(code).trim().replace(/^TMR1\./, '');
      let c;
      try { c = JSON.parse(decodeURIComponent(escape(atob(raw)))); } catch (e) { throw new Error('Неверный код'); }
      const clean = T.store.sanitize(c);
      if (!clean) throw new Error('Неверный код');
      return clean;
    },
    /* Код приходит от пользователя: принимаем только известные темы и ошибки, иначе панель учителя может сломаться. */
    sanitize(c) {
      if (!c || typeof c !== 'object' || c.v !== 1) return null;
      if (typeof c.s !== 'string' || c.s.length !== T.TOPICS.length || /[^migru]/.test(c.s)) return null;
      const name = typeof c.n === 'string' ? c.n.trim().slice(0, 40) : '';
      if (!name) return null;
      const own = (obj, k) => typeof k === 'string' && Object.prototype.hasOwnProperty.call(obj, k);
      const num = (x, max) => (Number.isFinite(x) && x >= 0 && x <= max ? Math.floor(x) : 0);
      return {
        v: 1,
        n: name,
        g: T.GOALS.some(g => g.id === c.g) ? c.g : 'full',
        t: num(c.t, 4102444800000) || Date.now(),
        s: c.s,
        r: Array.isArray(c.r) ? [...new Set(c.r.filter(id => own(T.TOPIC, id)))] : [],
        m: Array.isArray(c.m) ? c.m.filter(x => Array.isArray(x) && own(T.MISCONCEPTIONS, x[0])).map(x => [x[0], num(x[1], 1000) || 1]) : [],
        a: num(c.a, 1000),
        demo: c.demo === true
      };
    },
    imported() { return read(KEY_IMPORTED).map(c => T.store.sanitize(c)).filter(Boolean); },
    addImported(c) { const all = read(KEY_IMPORTED).filter(x => !(x.n === c.n && x.t === c.t)); all.push(c); write(KEY_IMPORTED, all); },
    clearImported() { write(KEY_IMPORTED, []); }
  };
})();
