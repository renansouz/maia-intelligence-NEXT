import { fetchHistorico } from '../../core/api.js';

export async function renderGestorDashboard() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div></div>`;

    try {
        const [historico, fazendasRes, coberturaRes] = await Promise.all([
            fetchHistorico(),
            fetch('/fazendas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(res => res.ok ? res.json() : []).catch(() => []),
            fetch('/cobertura/minha', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(res => res.ok ? res.json() : []).catch(() => [])
        ]);

        const fazendas = fazendasRes || [];
        const cobertura = coberturaRes || [];
        const criticosOuAtencao = historico.filter(d => d.CLASSIFICACAO === 'ALTO' || d.CLASSIFICACAO === 'MEDIO').length;

        container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-500">
                
                <!-- 1. NÚMEROS-CHAVE -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
                    <div class="bg-blue-50 border border-blue-100 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-blue-900 uppercase tracking-wider">Atenção / Crítico</span>
                            <div class="p-2 bg-blue-100 rounded-xl text-blue-900">
                                <i data-lucide="alert-triangle" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-blue-900">${criticosOuAtencao}</div>
                            <p class="text-xs text-blue-700 mt-1 font-medium">Máquinas exigindo monitoramento</p>
                        </div>
                    </div>

                    <div onclick="window.location.hash='#gestor/tickets'" class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between cursor-pointer hover:border-gray-400 transition">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Tickets Pendentes</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="message-square-warning" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-gray-900">2</div>
                            <p class="text-xs text-gray-500 mt-1 font-medium">Relatos da equipe aguardando ação</p>
                        </div>
                    </div>

                    <div class="relative group bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between cursor-pointer hover:border-blue-900 transition">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Cobertura Contratada</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="shield-check" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-lg font-black text-gray-900 truncate">Apólice Ativa</div>
                            <p class="text-xs text-blue-900 mt-1 font-semibold underline">Passe o mouse para ver os itens</p>
                        </div>
                        <div class="absolute bottom-full left-0 mb-3 hidden group-hover:block w-72 bg-gray-900 text-white text-xs rounded-xl p-4 shadow-2xl z-50 pointer-events-none">
                            <p class="font-bold text-emerald-400 mb-2 uppercase tracking-wider text-[10px]">Itens Cobertos na Apólice:</p>
                            <ul class="space-y-1.5">
                                ${cobertura.length === 0 ? `
                                    <li>• Incêndio, Raio e Explosão</li>
                                    <li>• Colisão e Tombamento</li>
                                    <li>• Danos em Transporte</li>
                                ` : cobertura.map(c => `
                                    <li>• <strong>${c.nome || c}</strong> ${c.itens ? ': ' + c.itens.join(', ') : ''}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- 2. CARDS DAS FAZENDAS (Com Drill-down ao clicar) -->
                <div class="space-y-4">
                    <div class="flex justify-between items-end">
                        <div>
                            <h3 class="text-xl font-extrabold text-[#101828] tracking-tight">Suas Propriedades</h3>
                            <p class="text-gray-500 text-sm">Clique em uma propriedade para inspecionar máquinas e operadores em operação.</p>
                        </div>
                    </div>

                    ${fazendas.length === 0 ? `
                        <div class="bg-white border border-gray-200 rounded-2xl p-10 text-center space-y-3 shadow-sm">
                            <i data-lucide="home" class="w-12 h-12 mx-auto text-gray-300"></i>
                            <h4 class="font-bold text-gray-800 text-base">Nenhuma propriedade cadastrada</h4>
                            <p class="text-sm text-gray-500 max-w-md mx-auto">Você ainda não possui propriedades cadastradas no sistema.</p>
                        </div>
                    ` : `
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            ${fazendas.map(f => `
                                <div id="fazenda-card-${f.id_fazenda}" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-4">
                                    <div class="view-mode">
                                        <div class="flex justify-between items-start mb-2">
                                            <span class="text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-900 px-2.5 py-1 rounded-md border border-blue-100">ID: ${f.id_fazenda}</span>
                                            <button onclick="ativarEdicaoFazenda(${f.id_fazenda})" class="text-xs font-bold text-blue-900 hover:underline flex items-center gap-1">
                                                <i data-lucide="edit-3" class="w-3.5 h-3.5"></i> Editar
                                            </button>
                                        </div>
                                        <h4 class="text-lg font-black text-gray-900 fazenda-nome-view">${f.nome}</h4>
                                        <p class="text-xs text-gray-500 mt-1 fazenda-end-view">${f.endereco || 'Endereço não especificado'}</p>
                                    </div>

                                    <!-- Formulário de Edição Inline -->
                                    <div class="edit-mode hidden space-y-3 pt-2 border-t border-gray-100">
                                        <input type="text" id="edit-nome-${f.id_fazenda}" value="${f.nome}" class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs outline-none focus:ring-2 focus:ring-blue-900">
                                        <input type="text" id="edit-end-${f.id_fazenda}" value="${f.endereco || ''}" placeholder="Endereço / Localidade" class="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-xs outline-none focus:ring-2 focus:ring-blue-900">
                                        <div class="flex gap-2">
                                            <button onclick="salvarEdicaoFazenda(${f.id_fazenda})" class="flex-1 bg-emerald-700 text-white py-1.5 rounded-lg font-bold text-xs hover:bg-emerald-800 transition">Salvar</button>
                                            <button onclick="cancelarEdicaoFazenda(${f.id_fazenda})" class="flex-1 bg-gray-200 text-gray-700 py-1.5 rounded-lg font-bold text-xs hover:bg-gray-300 transition">Cancelar</button>
                                        </div>
                                    </div>

                                    <div class="pt-4 border-t border-gray-100 flex justify-between items-center view-mode">
                                        <span class="text-xs font-semibold text-gray-600">Status Operacional</span>
                                        <button onclick="abrirDetalheFazenda(${f.id_fazenda}, '${f.nome}', '${f.endereco || ''}')" class="text-xs font-bold text-blue-900 hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 transition">
                                            Ver Máquinas & Equipe →
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>

                <!-- 3. FROTA MONITORADA DO GESTOR -->
                <div class="space-y-4">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <div>
                            <h3 class="text-xl font-extrabold text-[#101828] tracking-tight">Equipamentos da Frota</h3>
                            <p class="text-gray-500 text-sm">Clique em qualquer linha para abrir o Detalhes e solicitar manutenção.</p>
                        </div>
                        <div class="relative w-full sm:w-64">
                            <input type="text" id="busca-frota" placeholder="Filtrar por ID..." 
                                class="w-full bg-white border border-gray-300 rounded-lg pl-9 pr-4 py-2 text-xs outline-none focus:ring-2 focus:ring-blue-900 transition">
                            <i data-lucide="search" class="absolute left-3 top-2.5 w-3.5 h-3.5 text-gray-400"></i>
                        </div>
                    </div>
                    
                    <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Equipamento</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Localidade</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Classificação</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Score</th>
                                        <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                    </tr>
                                </thead>
                                <tbody id="tabela-frota-corpo" class="bg-white divide-y divide-gray-100">
                                    <!-- Renderizado via JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>

            <!-- Modal de Drill-down da Fazenda -->
            <div id="fazenda-detalhe-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
                    <div class="flex justify-between items-center border-b pb-3">
                        <div>
                            <h4 class="font-extrabold text-gray-900 text-lg" id="modal-fazenda-titulo">Fazenda</h4>
                            <p class="text-xs text-gray-500" id="modal-fazenda-end">Endereço</p>
                        </div>
                        <button onclick="document.getElementById('fazenda-detalhe-modal').classList.add('hidden')" class="text-gray-400 hover:text-gray-700"><i data-lucide="x" class="w-5 h-5"></i></button>
                    </div>
                    <div id="modal-fazenda-corpo" class="space-y-4 text-sm text-gray-700">
                        <!-- Injetado via JS -->
                    </div>
                </div>
            </div>
        `;

        lucide.createIcons();

        const inputBusca = document.getElementById('busca-frota');
        if (inputBusca) {
            inputBusca.oninput = (e) => {
                const termo = e.target.value.trim().toUpperCase();
                const filtrados = historico.filter(m => m.EQUIPAMENTO_ID.toUpperCase().includes(termo));
                renderizarTabelaFrota(filtrados);
            };
        }
        renderizarTabelaFrota(historico);

    } catch (error) {
        container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar painel do gestor.</p>`;
    }
}

function renderizarTabelaFrota(lista) {
    const corpo = document.getElementById('tabela-frota-corpo');
    if (!corpo) return;

    if (lista.length === 0) {
        corpo.innerHTML = `<tr><td colspan="5" class="py-10 text-center text-gray-400 italic text-sm">Nenhum equipamento encontrado.</td></tr>`;
        return;
    }

    corpo.innerHTML = lista.map(m => `
        <tr onclick="window.location.hash='#detalhe?eqp=${m.EQUIPAMENTO_ID}'" class="hover:bg-gray-50 transition cursor-pointer">
            <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${m.EQUIPAMENTO_ID}</td>
            <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${m.CIDADE || '---'}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${getBadge(m.CLASSIFICACAO)}">
                    ${m.CLASSIFICACAO}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-xs font-mono font-bold">${(m.PROBABILIDADE_ALTO * 100).toFixed(1)}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
                <span class="text-xs font-bold text-blue-900 hover:underline">Ver Detalhes →</span>
            </td>
        </tr>
    `).join('');
}

function getBadge(cls) {
    if (cls === 'ALTO') return 'bg-red-50 text-red-700 border-red-200';
    if (cls === 'MEDIO') return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-emerald-50 text-emerald-700 border-emerald-200';
}

// Funções globais de edição inline
window.ativarEdicaoFazenda = function (id) {
    const card = document.getElementById(`fazenda-card-${id}`);
    if (!card) return;
    card.querySelectorAll('.view-mode').forEach(el => el.classList.add('hidden'));
    card.querySelector('.edit-mode').classList.remove('hidden');
};

window.cancelarEdicaoFazenda = function (id) {
    const card = document.getElementById(`fazenda-card-${id}`);
    if (!card) return;
    card.querySelectorAll('.view-mode').forEach(el => el.classList.remove('hidden'));
    card.querySelector('.edit-mode').classList.add('hidden');
};

window.salvarEdicaoFazenda = function (id) {
    const inputNome = document.getElementById(`edit-nome-${id}`);
    const novoNome = inputNome.value.trim();
    const novoEnd = document.getElementById(`edit-end-${id}`).value.trim();

    if (!novoNome) {
        inputNome.classList.add('border-red-500', 'ring-2', 'ring-red-200');
        return;
    }

    const card = document.getElementById(`fazenda-card-${id}`);
    card.querySelector('.fazenda-nome-view').textContent = novoNome;
    card.querySelector('.fazenda-end-view').textContent = novoEnd || 'Endereço não especificado';

    window.cancelarEdicaoFazenda(id);
};

// Função de Drill-down da Fazenda (Mostra máquinas e operadores da propriedade)
window.abrirDetalheFazenda = async function (fazendaId, fazendaNome, fazendaEndereco) {
    const modal = document.getElementById('fazenda-detalhe-modal');
    document.getElementById('modal-fazenda-titulo').textContent = fazendaNome;
    document.getElementById('modal-fazenda-end').textContent = fazendaEndereco || 'Endereço não especificado';

    const corpo = document.getElementById('modal-fazenda-corpo');
    corpo.innerHTML = `<div class="flex justify-center py-10"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-900"></div></div>`;
    modal.classList.remove('hidden');
    lucide.createIcons();

    try {
        const res = await fetch('/maquinas', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        const todasMaquinas = res.ok ? await res.json() : [];

        // Filtra as máquinas vinculadas a esta fazenda
        const maquinasDaFazenda = todasMaquinas.filter(m => m.id_fazenda === fazendaId || m.ID_FAZENDA === fazendaId || m.fazenda_id === fazendaId);

        const promessas = maquinasDaFazenda.map(m =>
            fetch(`/maquinas/${m.equipamento_id || m.EQUIPAMENTO_ID}/detalhe`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
            }).then(res => res.ok ? res.json() : null).catch(() => null)
        );

        const detalhesMaquinas = await Promise.all(promessas);

        corpo.innerHTML = `
            <div class="space-y-4">
                <h5 class="text-xs font-bold text-gray-400 uppercase tracking-widest">Máquinas e Equipe na Propriedade (${detalhesMaquinas.length})</h5>
                ${detalhesMaquinas.length === 0 ? `
                    <p class="text-xs text-gray-400 italic bg-gray-50 p-6 rounded-xl text-center">Nenhum equipamento vinculado a esta fazenda no momento. Utilize o módulo de Cadastros e Vínculos para associar máquinas.</p>
                ` : `
                    <div class="space-y-3 max-h-72 overflow-y-auto">
                        ${detalhesMaquinas.map(m => {
            if (!m) return '';
            const operadorasStr = m.operadores && m.operadores.length > 0
                ? m.operadores.map(o => o.nome).join(', ')
                : 'Nenhum operador atribuído';

            const diag = m.diagnostico || { classificacao: 'REGULAR', score: 0 };

            return `
                                <div class="bg-gray-50 border border-gray-200 p-4 rounded-xl space-y-2 text-xs">
                                    <div class="flex justify-between items-center">
                                        <span class="font-black text-gray-900 text-sm">${m.equipamento_id}</span>
                                        <a href="#detalhe?eqp=${m.equipamento_id}" onclick="document.getElementById('fazenda-detalhe-modal').classList.add('hidden')" class="font-bold text-blue-900 hover:underline">Ver Detalhes →</a>
                                    </div>
                                    <div class="text-gray-600">${m.tipo || 'Ativo'} · ${m.modelo || 'Modelo N/D'}</div>
                                    <div class="pt-2 border-t border-gray-200 flex flex-col sm:flex-row justify-between gap-1 text-[11px]">
                                        <span class="text-gray-500">Operadores: <strong class="text-gray-800">${operadorasStr}</strong></span>
                                        <span class="font-bold text-blue-900">${diag.classificacao || 'REGULAR'}</span>
                                    </div>
                                </div>
                            `;
        }).join('')}
                    </div>
                `}
            </div>
        `;
        lucide.createIcons();
    } catch (e) {
        corpo.innerHTML = `<p class="text-xs text-red-500 text-center py-4">Erro ao carregar detalhes da fazenda.</p>`;
    }
};