import { exigirAutenticacao, getPapel, getNome, logout } from './auth.js';
import { renderseguradoraDashboard } from '../views/seguradora/dashboard.js';
import { renderGestorDashboard } from '../views/gestor/dashboard.js';
import { renderPainelOperador } from '../views/operador/painel.js';
import { renderGestorTickets } from '../views/gestor/tickets.js';
import { renderCompliance } from '../views/shared/compliance.js';
import { renderseguradoraCadastro } from '../views/seguradora/cadastros.js';
import { renderGestorCadastro } from '../views/gestor/cadastros.js';
import { renderDetalheMaquina } from '../views/shared/detalhe-maquina.js';
import { renderseguradoraSinistros } from '../views/seguradora/sinistros.js';
import { renderseguradoraGestores } from '../views/seguradora/gestores.js';
import { renderGestorOperadores } from '../views/gestor/operadores.js';

const CONFIG_PERFIS = {
  'seguradora': {
    classeFundo: 'bg-seguradora',
    classeTexto: 'text-seguradora',
    menus: [
      { id: '#seguradora/dashboard', label: 'Central de Risco' },
      { id: '#seguradora/sinistros', label: 'Sinistros' },
      { id: '#seguradora/compliance', label: 'Auditoria de Decisões' },
      { id: '#cadastros', label: 'Cadastros' }
    ],
    rotaInicial: '#seguradora/dashboard',
    textos: {
      titulo: 'Visão Executiva MAIA',
      subtitulo: 'Acompanhamento de risco sistêmico e auditoria de apólices em tempo real.'
    }
  },
  'GESTOR': {
    classeFundo: 'bg-gestor',
    classeTexto: 'text-gestor',
    menus: [
      { id: '#gestor/dashboard', label: 'Central' },
      { id: '#gestor/operadores', label: 'Operadores' },
      { id: '#gestor/tickets', label: 'Tickets da Equipe' },
      { id: '#cadastros', label: 'Cadastros' }
    ],
    rotaInicial: '#gestor/dashboard',
    textos: {
      titulo: 'Gestão de Frota e Segurança',
      subtitulo: 'Monitore o status dos seus equipamentos e evite sinistros.'
    }
  },
  'OPERADOR': {
    classeFundo: 'bg-operador',
    classeTexto: 'text-operador',
    menus: [
      { id: '#operador/painel', label: 'Minha Máquina' }
    ],
    rotaInicial: '#operador/painel',
    textos: {
      titulo: 'Painel do Operador',
      subtitulo: 'Verifique os alertas e registre problemas antes de iniciar sua operação.'
    }
  }
};

export function initRouter() {
  try {
    exigirAutenticacao();

    const papel = getPapel() || 'OPERADOR';
    const config = CONFIG_PERFIS[papel] || CONFIG_PERFIS['OPERADOR'];

    aplicarIdentidadeVisual(papel, config);
    construirMenu(config);
    configurarEventos();

    window.addEventListener('hashchange', () => resolverRota(config));

    if (!window.location.hash || window.location.hash === '') {
      window.location.hash = config.rotaInicial;
    } else {
      resolverRota(config);
    }
  } catch (e) {
    console.error("Erro fatal ao iniciar roteador:", e);
  }
}

function aplicarIdentidadeVisual(papel, config) {
  const nomeEl = document.getElementById('usuario-info');
  if (nomeEl) nomeEl.textContent = getNome() ? getNome().split(' ')[0] : 'Usuário';

  const logoText = document.getElementById('logo-text');
  if (logoText) logoText.className = `text-xl font-extrabold tracking-tighter ${config.classeTexto}`;

  const badge = document.getElementById('role-badge');
  if (badge) {
    badge.textContent = papel;
    badge.className = `hidden md:inline-block ml-2 px-2 py-0.5 text-[10px] font-bold uppercase rounded-full border ${config.classeTexto} border-current bg-white`;
  }

  const hero = document.getElementById('hero-section');
  if (hero) {
    hero.className = `${config.classeFundo} text-white py-12 px-4 transition-colors duration-500`;
  }

  const tituloEl = document.getElementById('hero-title');
  if (tituloEl) tituloEl.textContent = config.textos.titulo;

  const subEl = document.getElementById('hero-subtitle');
  if (subEl) subEl.textContent = config.textos.subtitulo;
}

function construirMenu(config) {
  const nav = document.getElementById('nav-menus');
  if (!nav) return;
  nav.innerHTML = config.menus.map(menu =>
    `<a href="${menu.id}" class="nav-link font-semibold text-gray-500 hover:${config.classeTexto} transition border-b-2 border-transparent px-2 py-1" data-target="${menu.id}">${menu.label}</a>`
  ).join('');
}

function configurarEventos() {
  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.onclick = (e) => {
      e.preventDefault();
      logout();
    };
  }
}

function resolverRota(config) {
  const hash = window.location.hash;
  const baseHash = hash.split('?')[0];

  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('data-target') === baseHash) {
      link.classList.remove('text-gray-500', 'border-transparent');
      link.style.color = '';
    } else {
      link.classList.add('text-gray-500', 'border-transparent');
    }
  });

  const contentArea = document.getElementById('view-content');
  if (!contentArea) return;

  const rotas = {
    '#seguradora/dashboard': renderseguradoraDashboard,
    '#seguradora/sinistros': renderseguradoraSinistros,
    '#seguradora/compliance': renderCompliance,
    '#seguradora/gestores': renderseguradoraGestores,
    '#gestor/dashboard': renderGestorDashboard,
    '#gestor/tickets': renderGestorTickets,
    '#operador/painel': renderPainelOperador,
    '#gestor/operadores': renderGestorOperadores,
    '#cadastros': () => {
      const papel = getPapel();
      if (papel === 'seguradora') renderseguradoraCadastro();
      else if (papel === 'GESTOR') renderGestorCadastro();
    },
    '#detalhe': renderDetalheMaquina
  };

  const renderFunc = rotas[baseHash];
  if (renderFunc) {
    renderFunc();
  } else {
    contentArea.innerHTML = `<p class="text-center py-10 text-gray-500">Página não encontrada.</p>`;
  }
}