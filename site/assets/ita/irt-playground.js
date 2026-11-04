// Interactive β3-IRT item characteristic curve, computed in the browser (no Python needed).
(() => {
  const root = document.querySelector('[data-playground]');
  if (!root) return;

  const svg = root.querySelector('[data-chart]');
  const readout = root.querySelector('[data-readout]');
  const inputs = Object.fromEntries(
    Array.from(root.querySelectorAll('[data-param]')).map((input) => [input.dataset.param, input]),
  );
  const outputs = Object.fromEntries(
    Array.from(root.querySelectorAll('[data-out]')).map((output) => [output.dataset.out, output]),
  );
  const defaults = Object.fromEntries(Object.entries(inputs).map(([key, input]) => [key, input.value]));

  const NS = 'http://www.w3.org/2000/svg';
  const W = 640;
  const H = 380;
  const M = { top: 20, right: 20, bottom: 48, left: 56 };
  const x = (theta) => M.left + theta * (W - M.left - M.right);
  const y = (p) => M.top + (1 - p) * (H - M.top - M.bottom);
  // β3-IRT: E[p] = 1 / (1 + (δ / (1 − δ))^a · ((1 − θ) / θ)^a), with θ and δ in (0, 1).
  const prob = (theta, delta, a) => {
    const t = Math.min(Math.max(theta, 1e-6), 1 - 1e-6);
    return 1 / (1 + ((delta / (1 - delta)) ** a) * (((1 - t) / t) ** a));
  };
  const fmt = (value, digits = 1) => value.toFixed(digits).replace('.', ',').replace(/^-/, '−');

  const el = (name, attrs = {}, text) => {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    return node;
  };

  const curvePath = (delta, a) => {
    const points = [];
    for (let i = 0; i <= 160; i += 1) {
      const theta = i / 160;
      points.push(`${i ? 'L' : 'M'}${x(theta).toFixed(1)},${y(prob(theta, delta, a)).toFixed(1)}`);
    }
    return points.join(' ');
  };

  // Static frame: grid, axes and labels.
  const frame = el('g', { class: 'pg-frame' });
  [0, 0.25, 0.5, 0.75, 1].forEach((p) => {
    frame.append(el('line', { x1: M.left, x2: W - M.right, y1: y(p), y2: y(p), class: p === 0.5 ? 'pg-half' : 'pg-grid' }));
    frame.append(el('text', { x: M.left - 10, y: y(p) + 4, class: 'pg-tick', 'text-anchor': 'end' }, fmt(p, 2)));
  });
  [0, 0.25, 0.5, 0.75, 1].forEach((t) => {
    frame.append(el('line', { x1: x(t), x2: x(t), y1: M.top, y2: H - M.bottom, class: 'pg-grid' }));
    frame.append(el('text', { x: x(t), y: H - M.bottom + 20, class: 'pg-tick', 'text-anchor': 'middle' }, fmt(t, 2)));
  });
  frame.append(el('text', { x: (M.left + W - M.right) / 2, y: H - 8, class: 'pg-label', 'text-anchor': 'middle' }, 'habilidade θ'));
  frame.append(el('text', { x: 14, y: (M.top + H - M.bottom) / 2, class: 'pg-label', 'text-anchor': 'middle', transform: `rotate(-90 14 ${(M.top + H - M.bottom) / 2})` }, 'resposta esperada'));
  svg.append(frame);

  const reference = el('path', { d: curvePath(0.5, 1), class: 'pg-reference' });
  const deltaLine = el('line', { class: 'pg-delta' });
  const curve = el('path', { class: 'pg-curve' });
  const guideX = el('line', { class: 'pg-guide' });
  const guideY = el('line', { class: 'pg-guide' });
  const marker = el('circle', { r: 7, class: 'pg-marker' });
  const markerLabel = el('text', { class: 'pg-marker-label' });
  svg.append(reference, deltaLine, curve, guideX, guideY, marker, markerLabel);

  const describe = (p, a) => {
    if (a < 0) return 'Discriminação negativa: quem tem mais habilidade acerta menos.';
    if (Math.abs(a) < 0.3) return 'Curva quase plana: o item quase não separa respondentes.';
    if (a < 1) return 'Com a entre 0 e 1, a curva vira um S deitado: muda rápido perto de 0 e de 1 e devagar no meio.';
    if (p > 0.85) return 'Para esse respondente, o item é fácil.';
    if (p < 0.15) return 'Para esse respondente, o item é difícil.';
    return 'Esse respondente está na região em que o item mais informa.';
  };

  const update = () => {
    const delta = Number(inputs.delta.value);
    const a = Number(inputs.a.value);
    const theta = Number(inputs.theta.value);
    const p = prob(theta, delta, a);

    outputs.delta.textContent = fmt(delta, 2);
    outputs.a.textContent = fmt(a);
    outputs.theta.textContent = fmt(theta, 2);

    curve.setAttribute('d', curvePath(delta, a));
    deltaLine.setAttribute('x1', x(delta));
    deltaLine.setAttribute('x2', x(delta));
    deltaLine.setAttribute('y1', y(0.5));
    deltaLine.setAttribute('y2', H - M.bottom);
    guideX.setAttribute('x1', x(theta));
    guideX.setAttribute('x2', x(theta));
    guideX.setAttribute('y1', y(p));
    guideX.setAttribute('y2', H - M.bottom);
    guideY.setAttribute('x1', M.left);
    guideY.setAttribute('x2', x(theta));
    guideY.setAttribute('y1', y(p));
    guideY.setAttribute('y2', y(p));
    marker.setAttribute('cx', x(theta));
    marker.setAttribute('cy', y(p));
    const labelLeft = x(theta) > W - 150;
    markerLabel.setAttribute('x', x(theta) + (labelLeft ? -12 : 12));
    markerLabel.setAttribute('y', y(p) - 12);
    markerLabel.setAttribute('text-anchor', labelLeft ? 'end' : 'start');
    markerLabel.textContent = `E[p] = ${fmt(p, 2)}`;

    readout.innerHTML = `Com θ = <strong>${fmt(theta, 2)}</strong>, a resposta esperada (probabilidade da classe correta) é <strong>${fmt(p, 2)}</strong>. ${describe(p, a)}`;
  };

  Object.values(inputs).forEach((input) => input.addEventListener('input', update));
  root.querySelector('[data-action="reset-playground"]').addEventListener('click', () => {
    Object.entries(defaults).forEach(([key, value]) => { inputs[key].value = value; });
    update();
  });
  update();
})();
