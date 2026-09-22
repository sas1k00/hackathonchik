/*
 * Отрисовка графа знаний в SVG. Базовые темы — внизу (корни), сложные — наверху.
 */
(function () {
  const T = window.Tamyr;
  const W = 1080, H = 660, NW = 164, NH = 50;

  function layout() {
    const levels = {};
    T.TOPICS.forEach(t => { (levels[t.level] = levels[t.level] || []).push(t.id); });
    const pos = {};
    const maxLevel = Math.max(...T.TOPICS.map(t => t.level));
    Object.keys(levels).forEach(l => {
      const ids = levels[l];
      const gap = W / (ids.length + 1);
      ids.forEach((id, i) => {
        pos[id] = { x: gap * (i + 1), y: H - 50 - (Number(l) * (H - 100) / maxLevel) };
      });
    });
    return pos;
  }
  const POS = layout();

  function el(name, attrs, text) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.keys(attrs || {}).forEach(k => e.setAttribute(k, attrs[k]));
    if (text != null) e.textContent = text;
    return e;
  }

  /* status: {topicId: STATUS}; opts: {current, rootGaps, highlight:Set, onClick} */
  T.renderGraph = function (container, status, opts) {
    opts = opts || {};
    const roots = new Set(opts.rootGaps || []);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, class: 'graph', role: 'img', 'aria-label': 'Карта знаний' });

    const edges = el('g', { class: 'edges' });
    T.TOPICS.forEach(t => {
      t.prereq.forEach(p => {
        const a = POS[t.id], b = POS[p];
        const y1 = a.y + NH / 2, y2 = b.y - NH / 2, my = (y1 + y2) / 2;
        const bad = status[t.id] === 'gap' && status[p] === 'gap';
        edges.appendChild(el('path', {
          d: `M${a.x},${y1} C${a.x},${my} ${b.x},${my} ${b.x},${y2}`,
          class: 'edge' + (bad ? ' edge-bad' : '')
        }));
      });
    });
    svg.appendChild(edges);

    T.TOPICS.forEach(t => {
      const p = POS[t.id];
      const st = status[t.id] || 'unknown';
      let cls = 'node n-' + st;
      if (roots.has(t.id)) cls += ' n-root';
      if (opts.current === t.id) cls += ' n-current';
      const g = el('g', { class: cls, transform: `translate(${p.x - NW / 2},${p.y - NH / 2})`, 'data-id': t.id });
      g.appendChild(el('title', {}, t.title));
      g.appendChild(el('rect', { width: NW, height: NH, rx: 12 }));
      g.appendChild(el('text', { x: NW / 2, y: NH / 2 + 6, 'text-anchor': 'middle' }, t.short));
      if (roots.has(t.id)) {
        g.appendChild(el('circle', { cx: NW - 4, cy: 4, r: 11, class: 'root-badge' }));
        g.appendChild(el('text', { x: NW - 4, y: 9, 'text-anchor': 'middle', class: 'root-badge-t' }, '!'));
      }
      if (opts.onClick) { g.style.cursor = 'pointer'; g.addEventListener('click', () => opts.onClick(t.id)); }
      svg.appendChild(g);
    });

    container.innerHTML = '';
    container.appendChild(svg);
  };

  T.LEGEND = [
    ['mastered', 'Освоено (проверено)'],
    ['inferred', 'Освоено (выведено)'],
    ['gap', 'Пробел'],
    ['root', 'Корневой пробел'],
    ['risk', 'Под угрозой'],
    ['unknown', 'Не проверялось']
  ];
})();
