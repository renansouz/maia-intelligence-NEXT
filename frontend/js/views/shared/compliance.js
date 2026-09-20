import { fetchHistorico } from '../../core/api.js';

let isProcessing = false;
let allData = [];
let filteredData = [];
let displayedCount = 50;

export async function renderCompliance() {
  if (isProcessing) return;
  isProcessing = true;

  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    const data = await fetchHistorico();
    allData = data.sort((a, b) => new Date(b.DATA_PREVISAO) - new Date(a.DATA_PREVISAO));
    filteredData = [...allData];
    displayedCount = 50;

    renderTableStructure(container);
    setupSearch();
    renderRows();

    lucide.createIcons();
  } catch (error) {
    container.innerHTML = `<p class="text-center py-10">Erro ao carregar auditoria.</p>`;
  } finally {
    isProcessing = false;
  }
}

function renderTableStructure(container) {
  container.innerHTML = `
        <div class="space-y-8 animate-in fade-in duration-500">
            <div class="border-b border-gray-100 pb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Registro de Auditoria de Decisões</h3>
                    <p class="text-gray-500 text-sm">Rastreabilidade imutável de decisões do Motor MAIA.</p>
                </div>
                
                <div class="flex gap-2 w-full md:w-auto">
                    <div class="relative flex-1 md:w-64">
                        <input type="text" id="search-input" placeholder="ID do Equipamento..." 
                            class="w-full bg-white border border-[#D0D5DD] rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A] transition">
                        <i data-lucide="search" class="absolute left-3 top-2.5 w-4 h-4 text-gray-400"></i>
                    </div>
                    <button id="btn-search" class="bg-[#101828] text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-black transition">
                        BUSCAR
                    </button>
                </div>
            </div>

            <div class="overflow-hidden border border-[#EAECF0] rounded-xl shadow-sm">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-[#F9FAFB]">
                        <tr>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-[#475467] uppercase">Data/Hora Previsão</th>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-[#475467] uppercase">Equipamento</th>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-[#475467] uppercase">Severidade</th>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-[#475467] uppercase">Score</th>
                            <th class="px-6 py-3 text-left text-[10px] font-bold text-[#475467] uppercase">Assinatura (Hash)</th>
                        </tr>
                    </thead>
                    <tbody id="compliance-tbody" class="bg-white divide-y divide-gray-100">
                    </tbody>
                </table>
            </div>
            <div id="pagination-area" class="flex justify-center pt-4"></div>
        </div>
    `;
  lucide.createIcons();
}

function setupSearch() {
  const btn = document.getElementById('btn-search');
  const input = document.getElementById('search-input');

  btn.onclick = () => {
    const term = input.value.trim().toUpperCase();
    filteredData = allData.filter(d => d.EQUIPAMENTO_ID.toUpperCase().includes(term));
    displayedCount = 50;

    document.getElementById('compliance-tbody').innerHTML = '';
    renderRows();
  };

  input.onkeypress = (e) => { if (e.key === 'Enter') btn.click(); };
}

function renderRows() {
  const tbody = document.getElementById('compliance-tbody');
  const paginationArea = document.getElementById('pagination-area');

  const start = tbody.children.length;
  const slice = filteredData.slice(start, displayedCount);

  if (filteredData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-10 text-center text-gray-400 italic">Nenhum equipamento encontrado com este termo.</td></tr>`;
    paginationArea.innerHTML = '';
    return;
  }

  const html = slice.map(row => `
        <tr onclick="window.location.hash='#detalhe?eqp=${row.EQUIPAMENTO_ID}'" class="hover:bg-[#F9FAFB] transition-colors cursor-pointer">
            <td class="px-6 py-4 whitespace-nowrap text-xs text-[#475467]">${new Date(row.DATA_PREVISAO).toLocaleString('pt-BR')}</td>
            <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-[#101828]">${row.EQUIPAMENTO_ID}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${getBadgeClass(row.CLASSIFICACAO)}">
                    ${row.CLASSIFICACAO}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-xs font-mono">${(row.PROBABILIDADE_ALTO * 100).toFixed(2)}%</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                    <span class="text-[10px] font-mono text-gray-300">${row.HASH_INTEGRIDADE.substring(0, 20)}...</span>
                    <i data-lucide="lock" class="w-3 h-3 text-gray-200"></i>
                </div>
            </td>
        </tr>
    `).join('');

  tbody.insertAdjacentHTML('beforeend', html);
  lucide.createIcons();

  if (displayedCount < filteredData.length) {
    paginationArea.innerHTML = `
            <button id="btn-load-more" class="text-sm font-bold text-[#DF082A] hover:bg-red-50 transition px-6 py-2 border border-[#EAECF0] rounded-full bg-white shadow-sm">
                Carregar mais 50 registros (${displayedCount} de ${filteredData.length})
            </button>
        `;
    document.getElementById('btn-load-more').onclick = () => {
      displayedCount += 50;
      renderRows();
    };
  } else {
    paginationArea.innerHTML = `<p class="text-xs text-gray-400 italic">Exibindo todos os ${filteredData.length} registros encontrados.</p>`;
  }
}

function getBadgeClass(cls) {
  if (cls === 'ALTO') return 'bg-red-50 text-[#D92D20] border-red-100';
  if (cls === 'MEDIO') return 'bg-amber-50 text-[#DC6803] border-amber-100';
  return 'bg-green-50 text-[#039855] border-green-100';
}