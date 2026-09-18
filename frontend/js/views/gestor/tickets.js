export async function renderGestorTickets() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div></div>`;

    try {
        const res = await fetch('/tickets', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        const tickets = res.ok ? await res.json() : [];

        const abertosCount = tickets.filter(t => t.status === 'ABERTO').length;

        container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <div class="border-b border-gray-100 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Tickets e Alertas da Equipe</h3>
                        <p class="text-gray-500 text-sm"><strong class="text-blue-900">${abertosCount}</strong> tickets em aberto exigindo acompanhamento.</p>
                    </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Data/Hora</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Equipamento</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Categoria</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Observação</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Status</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${tickets.length === 0 ? `
                                    <tr><td colspan="6" class="py-12 text-center text-gray-400 italic text-sm">Nenhum ticket registrado no momento.</td></tr>
                                ` : tickets.map(t => `
                                    <tr class="hover:bg-gray-50 transition">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-500">${new Date(t.criado_em).toLocaleString('pt-BR')}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${t.equipamento_id}</td>
                                        <td class="px-6 py-4 whitespace-nowrap"><span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-900 border border-blue-100">${t.categoria}</span></td>
                                        <td class="px-6 py-4 text-xs text-gray-700 max-w-xs truncate">${t.observacao}</td>
                                        <td class="px-6 py-4 whitespace-nowrap"><span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${getTicketBadge(t.status)}">${t.status}</span></td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right">
                                            <button onclick="abrirDetalheTicket(${t.id_ticket})" class="text-xs font-bold text-blue-900 hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 transition">
                                                Ver mais →
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Modal de Detalhe do Ticket -->
            <div id="ticket-detalhe-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
                    <div class="flex justify-between items-center border-b pb-3">
                        <h4 class="font-extrabold text-gray-900 text-lg">Detalhes do Relato</h4>
                        <button onclick="fecharModalTicket()" class="text-gray-400 hover:text-gray-700"><i data-lucide="x" class="w-5 h-5"></i></button>
                    </div>
                    <div id="conteudo-modal-ticket" class="space-y-4 text-sm text-gray-700">
                        <!-- Injetado dinamicamente -->
                    </div>
                </div>
            </div>
        `;
        lucide.createIcons();

    } catch (error) {
        container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar tickets da equipe.</p>`;
    }
}

function getTicketBadge(status) {
    if (status === 'ABERTO') return 'bg-amber-50 text-amber-800 border border-amber-200';
    if (status === 'RESOLVIDO') return 'bg-emerald-50 text-emerald-800 border border-emerald-200';
    return 'bg-blue-50 text-blue-800 border border-blue-200';
}

window.abrirDetalheTicket = async function (idTicket) {
    const modal = document.getElementById('ticket-detalhe-modal');
    const conteudo = document.getElementById('conteudo-modal-ticket');
    conteudo.innerHTML = `<div class="flex justify-center py-10"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-900"></div></div>`;
    modal.classList.remove('hidden');

    try {
        const res = await fetch(`/tickets/${idTicket}/detalhe`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        if (!res.ok) throw new Error("Erro ao buscar detalhes do ticket.");
        const t = await res.json();

        conteudo.innerHTML = `
            <div class="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-xl text-xs">
                <div><strong class="text-gray-400 block uppercase">Equipamento</strong> ${t.equipamento_id}</div>
                <div><strong class="text-gray-400 block uppercase">Operador</strong> ${t.operador_nome || 'N/D'}</div>
                <div><strong class="text-gray-400 block uppercase">Categoria</strong> ${t.categoria}</div>
                <div><strong class="text-gray-400 block uppercase">Data</strong> ${new Date(t.criado_em).toLocaleString('pt-BR')}</div>
            </div>
            <div>
                <strong class="text-xs text-gray-400 block uppercase mb-1">Observação Relatada</strong>
                <p class="bg-white p-3 rounded-xl border border-gray-200 text-xs text-gray-800 leading-relaxed">${t.observacao}</p>
            </div>
            <div class="pt-4 border-t flex gap-3">
                ${t.status === 'ABERTO' ? `
                    <button onclick="resolverTicket(${t.id_ticket})" class="flex-1 bg-emerald-700 text-white py-2.5 rounded-xl font-bold hover:bg-emerald-800 transition text-xs">
                        Marcar como Resolvido
                    </button>
                    <button onclick="escalarTicket(${t.id_ticket})" class="flex-1 bg-blue-900 text-white py-2.5 rounded-xl font-bold hover:bg-blue-950 transition text-xs">
                        Encaminhar para Sompo
                    </button>
                ` : `
                    <div class="w-full text-center text-xs font-bold text-gray-500 py-2">Este ticket já foi encerrado ou escalado.</div>
                `}
            </div>
        `;
        lucide.createIcons();
    } catch (e) {
        conteudo.innerHTML = `<p class="text-red-500 text-center py-4">Erro ao carregar detalhes.</p>`;
    }
};

window.fecharModalTicket = function () {
    document.getElementById('ticket-detalhe-modal').classList.add('hidden');
};

window.resolverTicket = async function (idTicket) {
    try {
        const res = await fetch(`/tickets/${idTicket}/resolver`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        if (!res.ok) throw new Error("Erro ao resolver ticket.");
        fecharModalTicket();
        renderGestorTickets();
    } catch (e) {
        alert("Erro ao processar solicitação.");
    }
};

window.escalarTicket = async function (idTicket) {
    if (!confirm("Tem certeza que deseja encaminhar este ticket como sinistro para a Sompo?")) return;
    try {
        const res = await fetch(`/tickets/${idTicket}/encaminhar-sompo`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        if (!res.ok) throw new Error("Erro ao encaminhar ticket.");
        fecharModalTicket();
        renderGestorTickets();
    } catch (e) {
        alert("Erro ao processar solicitação.");
    }
};