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
    sessions() { return read(KEY); },
    encode(c) { return 'TMR1.' + btoa(unescape(encodeURIComponent(JSON.stringify(c)))); },
    decode(code) {
      const raw = code.trim().replace(/^TMR1\./, '');
      const c = JSON.parse(decodeURIComponent(escape(atob(raw))));
      if (c.v !== 1 || typeof c.s !== 'string' || c.s.length !== T.TOPICS.length) throw new Error('Неверный код');
      return c;
    },
    imported() { return read(KEY_IMPORTED); },
    addImported(c) { const all = read(KEY_IMPORTED).filter(x => !(x.n === c.n && x.t === c.t)); all.push(c); write(KEY_IMPORTED, all); },
    clearImported() { write(KEY_IMPORTED, []); }
  };
})();
