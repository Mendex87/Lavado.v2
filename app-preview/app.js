const screens = document.querySelectorAll('.screen');
const links = document.querySelectorAll('.nav-link');
const title = document.getElementById('screen-title');

const titles = {
  dashboard: 'Dashboard operativo',
  'new-process': 'Abrir proceso',
  'active-process': 'Proceso activo',
  stock: 'Stock de canteras'
};

links.forEach(link => {
  link.addEventListener('click', () => {
    const target = link.dataset.screen;
    links.forEach(l => l.classList.toggle('active', l === link));
    screens.forEach(screen => screen.classList.toggle('active', screen.id === target));
    title.textContent = titles[target] || 'Vista previa';
  });
});
