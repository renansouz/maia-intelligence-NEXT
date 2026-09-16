export async function renderGestorTickets() {
  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div></div>`;

  try {
    const response = await fetch('/tickets', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
    });

    const tickets = response.ok ? await response.json() : [];

    container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <div class="border-b border-gray-100 pb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Tickets e Alertas da Equipe</h3>
                        <p class="text-gray-500 text-sm">Acompanhe os relatos de campo enviados pelos operadores vinculados às suas fazendas.</p>
                    </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Data/Hora</th>
                                <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Equipamento</th>
                                <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Categoria</th>
                                <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Observação</th>
                                <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase">Ação</th>
                            </tr>
                        </thead>
                        <tbody id="tickets-tbody" class="bg-white divide-y divide-gray-100">
                            ${tickets.length === 0 ? `
                                <tr><td colspan="6" class="py-12 text-center text-gray-400 italic text-sm">Nenhum ticket pendente ou registrado no momento.</td></tr>
                            ` : tickets.map(t => `
                                <tr class="hover:bg-gray-50 transition">
                                    <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">${new Date(t.criado_em).toLocaleString('pt-BR')}</td>
                                    <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${t.equipamento_id}</td>
                                    <td class="px-6 py-4 whitespace-nowrap"><span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-800 border border-blue-100">${t.categoria}</span></td>
                                    <td class="px-6 py-4 text-xs text-gray-700 max-w-xs truncate">${t.observacao}</td>
                                    <td class="px-6 py-4 whitespace-nowrap"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-100">${t.status}</span></td>
                                    <td class="px-6 py-4 whitespace-nowrap text-right">
                                        <button onclick="resolverTicket(${t.id_ticket})" class="text-xs font-bold text-emerald-700 hover:text-emerald-900 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-100 transition">
                                            Marcar Resolvido
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    lucide.createIcons();
  } catch (error) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar tickets.</p>`;
  }
}

// Função global simples para resolver o ticket
window.resolverTicket = async function (idTicket) {
  if (!confirm("Deseja marcar este ticket como resolvido?")) return;
  try {
    const res = await fetch(`/tickets/${idTicket}/resolver`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
    });
    if (!res.ok) throw new Error("Erro ao atualizar ticket.");
    alert("Ticket resolvido com sucesso!");
    renderGestorTickets();
  } catch (e) {
    alert("Erro ao processar solicitação.");
  }
};