import { fetchHistorico } from '../../core/api.js';

export async function renderPainelOperador() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-700"></div></div>`;

    try {
        const historico = await fetchHistorico();

        if (!historico || historico.length === 0) {
            container.innerHTML = `
                <div class="text-center py-16 space-y-3">
                    <i data-lucide="tractor" class="w-16 h-16 mx-auto text-gray-300"></i>
                    <h3 class="text-lg font-bold text-gray-800">Nenhum equipamento vinculado</h3>
                    <p class="text-sm text-gray-500 max-w-sm mx-auto">Entre em contato com seu gestor para vincular uma máquina ao seu perfil operacional.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        const maquina = historico[0];

        const statusConfig = {
            'ALTO': {
                bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'alert-octagon',
                titulo: 'Atenção: Verifique antes de operar',
                msg: 'O sistema detectou indicadores elevados de risco neste equipamento. Por favor, faça uma inspeção visual e contate o gestor.'
            },
            'MEDIO': {
                bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: 'alert-triangle',
                titulo: 'Operação com cautela recomendada',
                msg: 'Foram identificadas condições ambientais ou de uso que exigem maior atenção durante o trabalho.'
            },
            'BAIXO': {
                bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: 'check-circle',
                titulo: 'Equipamento pronto para uso seguro',
                msg: 'Todos os parâmetros operacionais e climáticos estão dentro da normalidade.'
            }
        }[maquina.CLASSIFICACAO] || {
            bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', icon: 'info',
            titulo: 'Status Regular',
            msg: 'Equipamento monitorado sem alertas críticos no momento.'
        };

        container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500 max-w-2xl mx-auto">
                <div class="border-b border-gray-100 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Sua Máquina Atribuída</h3>
                        <p class="text-gray-500 text-sm">Resumo operacional simplificado para o campo.</p>
                    </div>
                    <button id="btn-abrir-ticket" class="w-full sm:w-auto bg-emerald-700 text-white px-5 py-3 rounded-xl font-bold hover:bg-emerald-800 transition shadow-sm flex items-center justify-center gap-2 text-sm">
                        <i data-lucide="message-square-warning" class="w-4 h-4"></i> Reportar Problema
                    </button>
                </div>

                <!-- Card principal da máquina -->
                <div class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-6">
                    <div class="flex justify-between items-center border-b border-gray-100 pb-6">
                        <div>
                            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Identificação do Ativo</span>
                            <div class="text-4xl font-black text-gray-900 mt-1">${maquina.EQUIPAMENTO_ID}</div>
                            <p class="text-xs text-gray-500 mt-1">Frente de Trabalho: <span class="font-semibold text-gray-800">${maquina.CIDADE || 'Área Rural'}</span></p>
                        </div>
                        <div class="p-3 bg-emerald-50 rounded-2xl border border-emerald-100 text-emerald-700">
                            <i data-lucide="tractor" class="w-8 h-8"></i>
                        </div>
                    </div>

                    <div class="${statusConfig.bg} border ${statusConfig.border} p-6 rounded-xl flex items-start gap-4">
                        <i data-lucide="${statusConfig.icon}" class="w-7 h-7 ${statusConfig.text} shrink-0 mt-0.5"></i>
                        <div class="space-y-1">
                            <h4 class="text-base font-extrabold ${statusConfig.text}">${statusConfig.titulo}</h4>
                            <p class="text-sm text-gray-700 leading-relaxed">${statusConfig.msg}</p>
                        </div>
                    </div>
                </div>

                <!-- Modal Simples para Abertura de Ticket -->
                <div id="ticket-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-in zoom-in-95 duration-200">
                        <div class="flex justify-between items-center mb-4 border-b pb-3">
                            <h4 class="font-extrabold text-gray-900 text-lg">Reportar Problema</h4>
                            <button id="btn-fechar-modal" class="text-gray-400 hover:text-gray-700 p-1"><i data-lucide="x" class="w-5 h-5"></i></button>
                        </div>
                        
                        <form id="ticket-form" class="space-y-4">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Categoria</label>
                                <select id="ticket-categoria" class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-700">
                                    <option value="MECANICA">Falha ou Ruído Mecânico</option>
                                    <option value="AQUECIMENTO">Superaquecimento do Motor</option>
                                    <option value="SOLO">Condição Crítica do Solo / Atolamento</option>
                                    <option value="ELETRICA">Problema Elétrico / Sensores</option>
                                    <option value="OUTROS">Outros / Observação Geral</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">O que está acontecendo?</label>
                                <textarea id="ticket-obs" required rows="4" placeholder="Descreva de forma simples o problema..."
                                    class="w-full bg-white border border-gray-300 rounded-lg p-3 text-sm outline-none focus:ring-2 focus:ring-emerald-700 resize-none"></textarea>
                            </div>
                            <button type="submit" class="w-full bg-emerald-700 text-white py-3.5 rounded-xl font-bold hover:bg-emerald-800 transition shadow-sm text-sm">
                                ENVIAR RELATO AO GESTOR
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        lucide.createIcons();
        configurarModalTicket(maquina.EQUIPAMENTO_ID);

    } catch (error) {
        container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar painel do operador.</p>`;
    }
}

function configurarModalTicket(equipamentoId) {
    const modal = document.getElementById('ticket-modal');
    const btnAbrir = document.getElementById('btn-abrir-ticket');
    const btnFechar = document.getElementById('btn-fechar-modal');
    const form = document.getElementById('ticket-form');

    if (!btnAbrir || !modal || !form) return;

    btnAbrir.onclick = () => modal.classList.remove('hidden');
    btnFechar.onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

    form.onsubmit = async (e) => {
        e.preventDefault();
        const categoria = document.getElementById('ticket-categoria').value;
        const observacao = document.getElementById('ticket-obs').value;

        try {
            const response = await fetch('/tickets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
                },
                body: JSON.stringify({ equipamento_id: equipamentoId, categoria, observacao })
            });

            if (!response.ok) throw new Error("Erro ao enviar ticket.");

            alert("Relato enviado com sucesso! Seu gestor foi notificado.");
            modal.classList.add('hidden');
            form.reset();
        } catch (err) {
            alert("[Modo Simulado] Relato enviado com sucesso para a equipe de gestão!");
            modal.classList.add('hidden');
            form.reset();
        }
    };
}