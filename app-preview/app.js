const screens = document.querySelectorAll('.screen');
const links = document.querySelectorAll('.nav-link');
const title = document.getElementById('screen-title');
const toast = document.getElementById('toast');
const debugStatus = document.getElementById('debug-status');
const previewVersion = document.getElementById('preview-version');

const titles = {
  dashboard: 'Dashboard operativo',
  'new-process': 'Abrir proceso',
  'active-process': 'Proceso activo',
  stock: 'Stock de canteras',
  events: 'Eventos simulados'
};

const state = {
  operator: 'Diego',
  shift: 'Turno B',
  nextProcessNumber: 22,
  activeProcesses: {
    1: {
      code: 'PR-2026-00019',
      line: 1,
      mode: 'simple',
      quarries: ['Río Negro'],
      blendA: null,
      blendB: null,
      mainProduct: '30/70',
      cfgOutput: 'Producto 2',
      startedAt: '08:10',
      humidity: 6.8,
      readings: [
        { label: 'Entrada', partial: 128.0, totalizer: 8410.0 },
        { label: 'Salida 1', partial: 64.0, totalizer: 4210.0 },
        { label: 'Salida 2', partial: 32.0, totalizer: 2740.0 },
        { label: 'Salida 3', partial: 18.0, totalizer: 1130.0 },
      ],
    },
    2: {
      code: 'PR-2026-00021',
      line: 2,
      mode: 'blend',
      quarries: ['Dolavon', 'Río Negro'],
      blendA: 80,
      blendB: 20,
      mainProduct: 'Producto 4',
      cfgOutput: 'Descarte',
      startedAt: '09:31',
      humidity: 7.4,
      readings: [
        { label: 'Tolva A', partial: 84.0, totalizer: 12484.0 },
        { label: 'Tolva B real', partial: 21.0, totalizer: 6812.0 },
        { label: 'Salida principal', partial: 77.0, totalizer: 19304.0 },
        { label: 'Cfg Out', partial: 8.0, totalizer: 2115.0 },
      ],
    }
  },
  selectedProcessLine: 2,
  stock: [
    { name: 'Río Negro', tons: 420.0, lastMovement: 'Consumo proceso PR-2026-00019' },
    { name: 'Dolavon', tons: 75.0, lastMovement: 'Ajuste manual AJ-2026-0003' },
    { name: 'Trelew Norte', tons: 190.0, lastMovement: 'Ingreso camión ING-2026-0021' },
  ],
  alarms: [
    'L2, aviso sin proceso válido hace 3 min',
    'Stock bajo en cantera Dolavon',
  ],
  events: [
    '09:31 · Proceso PR-2026-00021 iniciado en Línea 2',
    '09:32 · Reset de parciales confirmado por operador',
    '10:05 · Stock Dolavon marcado como bajo',
  ]
};

function formatTon(v) { return `${v.toFixed(1)} t`; }
function activeProcess(line) { return state.activeProcesses[line] || null; }
function screenJump(target) {
  links.forEach(l => l.classList.toggle('active', l.dataset.screen === target));
  screens.forEach(screen => screen.classList.toggle('active', screen.id === target));
  title.textContent = titles[target] || 'Vista previa';
}
function notify(msg) {
  toast.textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(notify.timer);
  notify.timer = setTimeout(() => toast.classList.add('hidden'), 2200);
}
function nowText() {
  return new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false });
}

links.forEach(link => link.addEventListener('click', () => screenJump(link.dataset.screen)));
document.querySelectorAll('[data-screen-jump]').forEach(btn => btn.addEventListener('click', () => screenJump(btn.dataset.screenJump)));

function renderLineCard(line) {
  const p = activeProcess(line);
  if (!p) return;
  const prefix = `l${line}`;
  document.getElementById(`${prefix}-badge`).className = 'badge green';
  document.getElementById(`${prefix}-badge`).textContent = 'Proceso activo';
  document.getElementById(`${prefix}-operator`).textContent = `${state.shift} · ${state.operator}`;
  document.getElementById(`${prefix}-mode`).textContent = p.mode === 'blend' ? 'Blend' : 'Simple';
  document.getElementById(`${prefix}-quarries`).textContent = p.quarries.join(' + ');
  if (line === 1) {
    document.getElementById('l1-product').textContent = p.mainProduct;
    document.getElementById('l1-entry').textContent = formatTon(p.readings[0].partial);
    document.getElementById('l1-out1').textContent = formatTon(p.readings[1].partial);
    document.getElementById('l1-out2').textContent = formatTon(p.readings[2].partial);
    document.getElementById('l1-out3').textContent = formatTon(p.readings[3].partial);
  } else {
    document.getElementById('l2-blend').textContent = p.mode === 'blend' ? `${p.blendA} / ${p.blendB}` : 'Simple';
    document.getElementById('l2-in-a').textContent = formatTon(p.readings[0].partial);
    document.getElementById('l2-in-b').textContent = formatTon(p.readings[1].partial);
    document.getElementById('l2-out-main').textContent = formatTon(p.readings[2].partial);
    document.getElementById('l2-out-cfg').textContent = formatTon(p.readings[3].partial);
  }
}

function renderDashboard() {
  renderLineCard(1);
  renderLineCard(2);

  const alarmList = document.getElementById('alarm-list');
  alarmList.innerHTML = '';
  state.alarms.forEach((alarm, idx) => {
    const li = document.createElement('li');
    li.innerHTML = `<span><span class="severity ${idx === 0 ? 'red' : 'yellow'}"></span>${alarm}</span>`;
    alarmList.appendChild(li);
  });
  document.getElementById('alarm-count').textContent = String(state.alarms.length);

  const stockSummary = document.getElementById('stock-summary-list');
  stockSummary.innerHTML = '';
  state.stock.forEach(s => {
    const li = document.createElement('li');
    const klass = s.tons <= 80 ? 'warn' : '';
    li.innerHTML = `<span>${s.name}</span><strong class="${klass}">${formatTon(s.tons)}</strong>`;
    stockSummary.appendChild(li);
  });
}

function renderProcessTabs() {
  const wrap = document.getElementById('process-line-tabs');
  if (!wrap) return;
  wrap.innerHTML = '';
  [1, 2].forEach(line => {
    if (!activeProcess(line)) return;
    const btn = document.createElement('button');
    btn.className = `btn ${state.selectedProcessLine === line ? 'primary' : 'secondary'}`;
    btn.textContent = `Línea ${line}`;
    btn.addEventListener('click', () => {
      state.selectedProcessLine = line;
      renderProcess();
    });
    wrap.appendChild(btn);
  });
}

function renderProcess() {
  renderProcessTabs();
  const p = activeProcess(state.selectedProcessLine) || activeProcess(1) || activeProcess(2);
  if (!p) return;
  state.selectedProcessLine = p.line;
  document.getElementById('process-code').textContent = `Proceso ${p.code}`;
  document.getElementById('process-line').textContent = `Línea ${p.line}`;
  document.getElementById('process-operator').textContent = state.operator;
  document.getElementById('process-shift').textContent = state.shift;
  document.getElementById('process-start').textContent = p.startedAt;
  document.getElementById('process-quarries').textContent = p.quarries.join(' + ');
  document.getElementById('process-mode').textContent = p.mode === 'blend' ? 'Blend' : 'Simple';
  document.getElementById('process-target').textContent = p.mode === 'blend' ? `${p.blendA} / ${p.blendB}` : 'Simple';
  document.getElementById('process-cfg-output').textContent = p.cfgOutput;
  document.getElementById('humidity-value').textContent = `${p.mainProduct}, ${p.humidity.toFixed(1)}%`;

  const body = document.getElementById('live-table-body');
  body.innerHTML = '';
  p.readings.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.label}</td><td>${formatTon(r.partial)}</td><td>${formatTon(r.totalizer)}</td>`;
    body.appendChild(tr);
  });
}

function renderStock() {
  const body = document.getElementById('stock-table-body');
  body.innerHTML = '';
  state.stock.forEach(s => {
    let badge = '<span class="badge blue">OK</span>';
    if (s.tons <= 80) badge = '<span class="badge yellow">Bajo</span>';
    if (s.tons <= 40) badge = '<span class="badge red">Crítico</span>';
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.name}</td><td>${formatTon(s.tons)}</td><td>${s.lastMovement}</td><td>${badge}</td>`;
    body.appendChild(tr);
  });
}

function renderEvents() {
  const list = document.getElementById('event-list');
  list.innerHTML = '';
  [...state.events].reverse().forEach(e => {
    const li = document.createElement('li');
    li.textContent = e;
    list.appendChild(li);
  });
}

function renderAll() {
  renderDashboard();
  renderProcess();
  renderStock();
  renderEvents();
}

function updateFormVisibility() {
  const mode = document.getElementById('form-mode').value;
  const line = document.getElementById('form-line').value;
  const showBlend = line === '2' && mode === 'blend';
  const line1 = line === '1';

  document.getElementById('form-mode').disabled = line1;
  if (line1) document.getElementById('form-mode').value = 'simple';

  ['group-quarry-b','group-blend-a','group-blend-b'].forEach(id => {
    document.getElementById(id).style.display = showBlend ? '' : 'none';
  });
}

function openProcess() {
  const line = Number(document.getElementById('form-line').value);
  if (activeProcess(line)) {
    notify(`La Línea ${line} ya tiene un proceso activo`);
    return;
  }

  const mode = line === 1 ? 'simple' : document.getElementById('form-mode').value;
  const qa = document.getElementById('form-quarry-a').value;
  const qb = document.getElementById('form-quarry-b').value;
  const mainProduct = document.getElementById('form-main-product').value;
  const cfgOutput = document.getElementById('form-cfg-output').value;
  const blendA = Number(document.getElementById('form-blend-a').value || 100);
  const blendB = Number(document.getElementById('form-blend-b').value || 0);
  const startedAt = nowText();

  state.activeProcesses[line] = {
    code: `PR-2026-${String(state.nextProcessNumber++).padStart(5,'0')}`,
    line,
    mode,
    quarries: mode === 'blend' ? [qa, qb] : [qa],
    blendA: mode === 'blend' ? blendA : null,
    blendB: mode === 'blend' ? blendB : null,
    mainProduct,
    cfgOutput,
    startedAt,
    humidity: 7.4,
    readings: line === 2 ? [
      { label: 'Tolva A', partial: 0.0, totalizer: 12484.0 },
      { label: mode === 'blend' ? 'Tolva B real' : 'Entrada', partial: 0.0, totalizer: 6812.0 },
      { label: 'Salida principal', partial: 0.0, totalizer: 19304.0 },
      { label: 'Cfg Out', partial: 0.0, totalizer: 2115.0 },
    ] : [
      { label: 'Entrada', partial: 0.0, totalizer: 8410.0 },
      { label: 'Salida 1', partial: 0.0, totalizer: 4210.0 },
      { label: 'Salida 2', partial: 0.0, totalizer: 2740.0 },
      { label: 'Salida 3', partial: 0.0, totalizer: 1130.0 },
    ],
  };

  state.selectedProcessLine = line;
  state.events.push(`${startedAt} · Proceso ${state.activeProcesses[line].code} iniciado en Línea ${line}`);
  state.events.push(`${startedAt} · Reset de parciales confirmado por operador`);
  renderAll();
  screenJump('active-process');
  notify('Proceso simulado abierto');
}

function simulateAdvance() {
  const p = activeProcess(state.selectedProcessLine) || activeProcess(1) || activeProcess(2);
  if (!p) return;

  const delta = 5;
  if (p.line === 2) {
    p.readings[0].partial += p.mode === 'blend' ? 4 : 5;
    p.readings[0].totalizer += p.mode === 'blend' ? 4 : 5;
    p.readings[1].partial += p.mode === 'blend' ? 1 : 0;
    p.readings[1].totalizer += p.mode === 'blend' ? 1 : 0;
    p.readings[2].partial += 3.8;
    p.readings[2].totalizer += 3.8;
    p.readings[3].partial += 0.4;
    p.readings[3].totalizer += 0.4;
    const quarryA = state.stock.find(s => s.name === p.quarries[0]);
    if (quarryA) { quarryA.tons = Math.max(0, quarryA.tons - (p.mode === 'blend' ? 4 : 5)); quarryA.lastMovement = `Consumo proceso ${p.code}`; }
    if (p.mode === 'blend') {
      const quarryB = state.stock.find(s => s.name === p.quarries[1]);
      if (quarryB) { quarryB.tons = Math.max(0, quarryB.tons - 1); quarryB.lastMovement = `Consumo proceso ${p.code}`; }
    }
  } else {
    p.readings[0].partial += delta;
    p.readings[0].totalizer += delta;
    p.readings[1].partial += 2.5;
    p.readings[1].totalizer += 2.5;
    p.readings[2].partial += 1.5;
    p.readings[2].totalizer += 1.5;
    p.readings[3].partial += 0.7;
    p.readings[3].totalizer += 0.7;
    const quarry = state.stock.find(s => s.name === p.quarries[0]);
    if (quarry) { quarry.tons = Math.max(0, quarry.tons - delta); quarry.lastMovement = `Consumo proceso ${p.code}`; }
  }
  state.events.push(`${nowText()} · Simulación de avance en ${p.code} (+5 t)`);
  if (state.stock.some(s => s.name === 'Dolavon' && s.tons <= 80) && !state.alarms.includes('Stock bajo en cantera Dolavon')) {
    state.alarms.push('Stock bajo en cantera Dolavon');
  }
  renderAll();
  notify('Producción simulada actualizada');
}

function closeProcess() {
  const p = activeProcess(state.selectedProcessLine) || activeProcess(1) || activeProcess(2);
  if (!p) return;
  state.events.push(`${nowText()} · Proceso ${p.code} cerrado por operador`);
  delete state.activeProcesses[p.line];
  state.selectedProcessLine = activeProcess(1) ? 1 : 2;
  notify('Proceso simulado cerrado');
  screenJump('dashboard');
  renderAll();
}

function registerEvent() {
  const p = activeProcess(state.selectedProcessLine) || activeProcess(1) || activeProcess(2);
  if (!p) return;
  state.events.push(`${nowText()} · Evento manual registrado en ${p.code}`);
  renderEvents();
  notify('Evento manual simulado');
}

function adjustStock() {
  const quarry = state.stock.find(s => s.name === 'Dolavon');
  quarry.tons += 25;
  quarry.lastMovement = 'Ajuste manual AJ-MOCK-0001';
  state.events.push(`${nowText()} · Ajuste de stock manual sobre Dolavon (+25 t)`);
  state.alarms = state.alarms.filter(a => a !== 'Stock bajo en cantera Dolavon');
  renderAll();
  notify('Stock ajustado en simulación');
}

function registerIngress() {
  const quarry = state.stock.find(s => s.name === 'Trelew Norte');
  quarry.tons += 40;
  quarry.lastMovement = 'Ingreso camión ING-MOCK-0007';
  state.events.push(`${nowText()} · Ingreso manual simulado en Trelew Norte (+40 t)`);
  renderAll();
  notify('Ingreso simulado registrado');
}

document.getElementById('form-line').addEventListener('change', updateFormVisibility);
document.getElementById('form-mode').addEventListener('change', updateFormVisibility);
document.getElementById('confirm-process-btn').addEventListener('click', openProcess);
document.getElementById('cancel-process-btn').addEventListener('click', () => { screenJump('dashboard'); notify('Apertura cancelada'); });
document.getElementById('simulate-btn').addEventListener('click', simulateAdvance);
document.getElementById('close-process-btn').addEventListener('click', closeProcess);
document.getElementById('register-event-btn').addEventListener('click', registerEvent);
document.getElementById('plc-detail-btn').addEventListener('click', () => notify('Detalle PLC simulado próximamente'));
document.getElementById('stock-adjust-btn').addEventListener('click', adjustStock);
document.getElementById('stock-in-btn').addEventListener('click', registerIngress);
document.getElementById('debug-test-btn').addEventListener('click', () => {
  debugStatus.textContent = 'JS OK, botón respondió';
  debugStatus.className = 'debug-ok';
  notify('JS funcionando');
});

updateFormVisibility();
renderAll();
debugStatus.textContent = 'JS cargado';
debugStatus.className = 'debug-ok';
previewVersion.textContent = 'Plant App Preview v0.4';