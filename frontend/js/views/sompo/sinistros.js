export async function renderSompoSinistros() {
  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    const res = await fetch('/tickets/sinistros', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
    });
    const sinistros = res.ok ? await res.json() : [];

    container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Sinistros e Ocorrências Escaladas</h3>
                    <p class="text-gray-500 text-sm">Acompanhamento de eventos graves encaminhados pelos gestores para regulação da seguradora.</p>
                </div>

                <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Data Escalado</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Equipamento</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Gestor</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Operador</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Categoria</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Observação</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${sinistros.length === 0 ? `
                                    <tr><td colspan="7" class="py-12 text-center text-gray-400 italic text-sm">Nenhum sinistro escalado no momento.</td></tr>
                                ` : sinistros.map(s => `
                                    <tr onclick="window.location.hash='#detalhe?eqp=${s.equipamento_id}'" class="hover:bg-gray-50 transition cursor-pointer">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">${s.escalado_em ? new Date(s.escalado_em).toLocaleString('pt-BR') : '---'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${s.equipamento_id}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-700">${s.gestor_nome || '---'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-700">${s.operador_nome || '---'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap"><span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-100">${s.categoria}</span></td>
                                        <td class="px-6 py-4 text-xs text-gray-700 max-w-xs truncate">${s.observacao}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right">
                                            <span class="text-xs font-bold text-[#DF082A] hover:underline">Ver Ativo →</span>
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
  } catch (e) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar sinistros da Sompo.</p>`;
  }
}