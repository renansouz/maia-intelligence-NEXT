import { fetchHistorico } from '../../core/api.js';

export async function renderGestorDashboard() {
  const container = document.getElementById('view-content');
  container.innerHTML = `
        <div class="flex flex-col justify-center items-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div>
            <p class="mt-4 text-gray-500 font-medium tracking-tight">Carregando painel de fazendas e frota...</p>
        </div>
    `;

  try {
    const [historico, fazendasRes] = await Promise.all([
      fetchHistorico(),
      fetch('/fazendas', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
      }).then(res => res.ok ? res.json() : []).catch(() => [])
    ]);

    const fazendas = fazendasRes || [];

    // Métricas do topo para o gestor
    const criticosOuAtencao = historico.filter(d => d.CLASSIFICACAO === 'ALTO' || d.CLASSIFICACAO === 'MEDIO').length;

    container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-500">
                
                <!-- 1. NÚMEROS-CHAVE DE DECISÃO DO GESTOR -->
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

                    <div class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
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

                    <div class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Cobertura Contratada</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="shield-check" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-lg font-black text-gray-900 truncate">Básica + Adicionais</div>
                            <p class="text-xs text-gray-500 mt-1 font-medium">Apólice Sompo Benfeitorias ativa</p>
                        </div>
                    </div>
                </div>

                <!-- 2. CARDS DAS FAZENDAS -->
                <div class="space-y-4">
                    <div class="flex justify-between items-end">
                        <div>
                            <h3 class="text-xl font-extrabold text-[#101828] tracking-tight">Suas Fazendas</h3>
                            <p class="text-gray-500 text-sm">Propriedades rurais cadastradas na sua gestão.</p>
                        </div>
                    </div>

                    ${fazendas.length === 0 ? `
                        <div class="bg-white border border-gray-200 rounded-2xl p-10 text-center space-y-3 shadow-sm">
                            <i data-lucide="home" class="w-12 h-12 mx-auto text-gray-300"></i>
                            <h4 class="font-bold text-gray-800 text-base">Nenhuma fazenda cadastrada</h4>
                            <p class="text-sm text-gray-500 max-w-md mx-auto">Você ainda não possui fazendas cadastradas no sistema.</p>
                        </div>
                    ` : `
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            ${fazendas.map(f => `
                                <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition flex flex-col justify-between space-y-4">
                                    <div>
                                        <div class="flex justify-between items-start mb-2">
                                            <span class="text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-900 px-2.5 py-1 rounded-md border border-blue-100">Fazenda ID: ${f.id_fazenda}</span>
                                            <i data-lucide="map-pin" class="w-4 h-4 text-blue-900"></i>
                                        </div>
                                        <h4 class="text-lg font-black text-gray-900">${f.nome}</h4>
                                        <p class="text-xs text-gray-500 mt-1">${f.endereco || 'Endereço não especificado'}</p>
                                    </div>
                                    <div class="pt-4 border-t border-gray-100 flex justify-between items-center">
                                        <span class="text-xs font-semibold text-gray-600">Status Operacional</span>
                                        <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100">Regular</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>

                <!-- 3. FROTA MONITORADA DO GESTOR -->
                <div class="space-y-4">
                    <h3 class="text-xl font-extrabold text-[#101828] tracking-tight">Equipamentos da Frota</h3>
                    <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Equipamento</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Localidade</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Classificação</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Score</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase">Ações</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${historico.length === 0 ? `
                                    <tr><td colspan="5" class="py-10 text-center text-gray-400 italic text-sm">Nenhum equipamento encontrado na sua frota.</td></tr>
                                ` : historico.map(m => `
                                    <tr class="hover:bg-gray-50 transition">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${m.EQUIPAMENTO_ID}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${m.CIDADE || '---'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${getBadge(m.CLASSIFICACAO)}">
                                                ${m.CLASSIFICACAO}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-mono font-bold">${(m.PROBABILIDADE_ALTO * 100).toFixed(1)}%</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right space-x-2">
                                            <a href="#diagnostico" class="text-xs font-bold text-blue-900 hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 transition inline-block">
                                                Laudo XAI
                                            </a>
                                            <button onclick="solicitarManutencao('${m.EQUIPAMENTO_ID}')" class="text-xs font-bold text-gray-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg border border-gray-300 transition">
                                                Pedir Manutenção
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        `;

    lucide.createIcons();

  } catch (error) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar painel do gestor.</p>`;
  }
}

function getBadge(cls) {
  if (cls === 'ALTO') return 'bg-red-50 text-red-700 border-red-200';
  if (cls === 'MEDIO') return 'bg-amber-50 text-amber-700 border-amber-200';
  return 'bg-emerald-50 text-emerald-700 border-emerald-200';
}

window.solicitarManutencao = async function (equipamentoId) {
  const desc = prompt(`Descreva o motivo da manutenção para o equipamento ${equipamentoId}:`);
  if (!desc) return;

  try {
    const res = await fetch('/manutencao/solicitar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
      },
      body: JSON.stringify({ equipamento_id: equipamentoId, descricao: desc })
    });

    if (!res.ok) throw new Error("Erro ao gerar link de manutenção.");
    const data = await res.json();
    alert(`Link gerado com sucesso para o técnico!\n\nURL de acesso:\nmanutencao.html?token=${data.token}`);
  } catch (e) {
    const tokenFake = Math.random().toString(36).substring(2);
    alert(`[Modo Simulado] Link gerado com sucesso!\n\nEnvie este link para o técnico:\nmanutencao.html?token=${tokenFake}`);
  }
};