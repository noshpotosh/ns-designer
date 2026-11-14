
// Board drawing, in millimetres.
(function () {
  const P = 17, inset = 0.9, gap = 20, half = 5 * P;
  const svg = document.getElementById('board');
  const ns = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs, text) => {
    const n = document.createElementNS(ns, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text) n.textContent = text;
    svg.appendChild(n);
    return n;
  };
  const legends = {
    L: [['Q','W','E','R','T'],['A','S','D','F','G'],['Z','X','C','V','B'],[null,null,'T1','T2','T3']],
    R: [['Y','U','I','O','P'],['H','J','K','L',';'],['N','M',',','.','/'],['T4','T5','T6',null,null]]
  };
  [['L', 0], ['R', half + gap]].forEach(([side, ox]) => {
    el('rect', { x: ox - 1.5, y: -1.5, width: half + 3, height: 4 * P + 3, rx: 2, fill: 'none', stroke: 'var(--key-edge)', 'stroke-width': 0.4 });
    for (let r = 0; r < 4; r++) for (let c = 0; c < 5; c++) {
      const label = legends[side][r][c];
      if (!label) continue;
      const x = ox + c * P, y = r * P;
      el('rect', { x: x + inset, y: y + inset, width: P - 2 * inset, height: P - 2 * inset, rx: 1.2, fill: 'var(--key)', stroke: 'var(--key-edge)', 'stroke-width': 0.35 });
      el('text', { x: x + P / 2, y: y + P / 2 + 1.4, 'text-anchor': 'middle', 'font-size': 4 }, label);
    }
    // XIAO: 21 x 17.8 mm, centred in the 2-key slot.
    const sx = side === 'L' ? ox : ox + 3 * P;
    const xx = sx + (2 * P - 21) / 2, xy = 3 * P + (P - 17.8) / 2;
    el('rect', { x: xx, y: xy, width: 21, height: 17.8, rx: 1, fill: 'var(--gold-soft)', stroke: 'var(--gold)', 'stroke-width': 0.45 });
    const usbX = side === 'L' ? xx - 1.2 : xx + 21 - 2.2;
    el('rect', { x: usbX, y: xy + 8.9 - 4.5, width: 3.4, height: 9, rx: 0.8, fill: 'var(--gold)' });
    el('text', { x: xx + 10.5, y: xy + 10.3, 'text-anchor': 'middle', 'font-size': 3.6, style: 'fill:var(--gold)' }, 'XIAO');
    el('text', { x: ox + half / 2, y: -4.5, 'text-anchor': 'middle', 'font-size': 3.6 }, side === 'L' ? 'LEFT' : 'RIGHT');
  });
  // Dimension line under the left half.
  const dy = 4 * P + 6;
  el('line', { x1: 0, y1: dy, x2: half, y2: dy, stroke: 'var(--muted)', 'stroke-width': 0.3 });
  el('line', { x1: 0, y1: dy - 1.5, x2: 0, y2: dy + 1.5, stroke: 'var(--muted)', 'stroke-width': 0.3 });
  el('line', { x1: half, y1: dy - 1.5, x2: half, y2: dy + 1.5, stroke: 'var(--muted)', 'stroke-width': 0.3 });
  el('text', { x: half / 2, y: dy + 5, 'text-anchor': 'middle', 'font-size': 3.6 }, '85 mm (5 × 17)');
})();

// Colorway switcher for the hero render.
document.querySelectorAll('[data-cw]').forEach(btn => {
  btn.addEventListener('click', () => {
    const img = document.getElementById('hero-shot');
    img.src = `assets/hero-${btn.dataset.cw}.png`;
    img.alt = `Open tray, three-quarter view, ${btn.dataset.cw} colorway`;
    document.querySelectorAll('[data-cw]').forEach(b => b.setAttribute('aria-pressed', b === btn));
  });
});

// Interactive viewer, loaded on demand.
document.querySelectorAll('[data-load]').forEach(btn => {
  btn.addEventListener('click', () => {
    const box = document.getElementById('viewer');
    if (location.protocol === 'file:') {
      box.innerHTML = '<p>The 3D viewer can\'t load from a file on disk. Run <code>npm run preview</code> in the repo root, then open <code>localhost:8000/ns-designer/</code>.</p>';
      return;
    }
    box.innerHTML = `<iframe src="viewer/index.html${btn.dataset.load}" title="Interactive 3D model" loading="lazy"></iframe>`;
  });
});

// Remember ticked phases in this browser only.
document.querySelectorAll('.phases input').forEach(box => {
  try { box.checked = localStorage.getItem('keeb-' + box.id) === '1'; } catch (e) {}
  box.addEventListener('change', () => {
    try { localStorage.setItem('keeb-' + box.id, box.checked ? '1' : '0'); } catch (e) {}
  });
});
