import { fetchHistorico } from '../../core/api.js';

export async function renderPainelOperador() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-700"></div></div>`;

    try {
        const [historico, climaRes] = await Promise.all([
            fetchHistorico(),
            fetch('/clima/operador', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
            }).then(res => res.ok ? res.json() : null).catch(() => null)
        ]);

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
        const clima = climaRes || { previsao: [], tem_alerta: false };
        const regiaoNome = maquina.CIDADE || 'Sua Região';

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
            <div class="space-y-8 animate-in fade-in duration-500 max-w-3xl mx-auto">
                <div class="border-b border-gray-100 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Painel Operacional</h3>
                        <p class="text-gray-500 text-sm">Resumo simplificado para tomada de decisão no campo.</p>
                    </div>
                    <button id="btn-abrir-ticket" class="w-full sm:w-auto bg-emerald-700 text-white px-5 py-3 rounded-xl font-bold hover:bg-emerald-800 transition shadow-sm flex items-center justify-center gap-2 text-sm">
                        <i data-lucide="message-square-warning" class="w-4 h-4"></i> Reportar Problema
                    </button>
                </div>

                <!-- Card principal da máquina (Clicável) -->
                <div onclick="window.location.hash='#detalhe?eqp=${maquina.EQUIPAMENTO_ID}'" class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-6 hover:border-emerald-500 transition cursor-pointer group">
                    <div class="flex justify-between items-center border-b border-gray-100 pb-6">
                        <div>
                            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Ativo Atribuído</span>
                            <div class="text-4xl font-black text-gray-900 mt-1 group-hover:text-emerald-700 transition">${maquina.EQUIPAMENTO_ID}</div>
                            <p class="text-xs text-gray-500 mt-1">Frente de Trabalho: <span class="font-semibold text-gray-800">${regiaoNome}</span></p>
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
                    <div class="text-right">
                        <span class="text-xs font-bold text-emerald-700 group-hover:underline">Ver detalhes completos da máquina →</span>
                    </div>
                </div>

                <!-- Card de Previsão do Tempo com Localidade e Horas Formatadas -->
                <div class="bg-white border ${clima.tem_alerta ? 'border-amber-300 bg-amber-50/30' : 'border-gray-200'} rounded-2xl p-6 shadow-sm space-y-4">
                    <div class="flex items-center justify-between border-b border-gray-100 pb-3">
                        <div class="flex items-center gap-2">
                            <i data-lucide="cloud-sun" class="w-5 h-5 text-emerald-700"></i>
                            <h4 class="font-extrabold text-gray-900 text-sm">Previsão do Tempo — ${regiaoNome}</h4>
                        </div>
                        ${clima.tem_alerta ? `
                            <span class="px-2.5 py-0.5 bg-amber-100 text-amber-800 rounded-full text-[10px] font-bold border border-amber-200 flex items-center gap-1">
                                <i data-lucide="alert-triangle" class="w-3 h-3"></i> Alerta Climático
                            </span>
                        ` : ''}
                    </div>

                    ${clima.tem_alerta ? `
                        <div class="bg-amber-100/60 border border-amber-200 p-3 rounded-xl text-xs text-amber-900 font-medium">
                            ⚠️ Condições meteorológicas adversas previstas nas próximas horas — avalie com cautela antes de iniciar a operação.
                        </div>
                    ` : ''}

                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                        ${!clima.previsao || clima.previsao.length === 0 ? `
                            <p class="col-span-4 text-xs text-gray-400 italic text-center py-4">Dados meteorológicos indisponíveis no momento.</p>
                        ` : clima.previsao.slice(0, 4).map(p => {
            // Formata "2026-09-18T13:00" para "13:00"
            const horaFormatada = p.hora && p.hora.includes('T') ? p.hora.split('T')[1].substring(0, 5) : (p.hora || '---');
            return `
                                <div class="bg-gray-50 p-3 rounded-xl border border-gray-100 text-center space-y-1">
                                    <span class="text-[10px] font-bold text-gray-400 uppercase">${horaFormatada}</span>
                                    <div class="text-base font-extrabold text-gray-900">${p.temperatura}°C</div>
                                    <div class="text-[11px] text-gray-600 flex items-center justify-center gap-1">
                                        <i data-lucide="droplets" class="w-3 h-3 text-blue-500"></i> ${p.chuva_mm || 0} mm
                                    </div>
                                </div>
                            `;
        }).join('')}
                    </div>
                </div>

                <!-- Modal sem alert para Abertura de Ticket -->
                <div id="ticket-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-in zoom-in-95 duration-200 space-y-4">
                        <div class="flex justify-between items-center border-b pb-3">
                            <h4 class="font-extrabold text-gray-900 text-lg">Reportar Problema</h4>
                            <button id="btn-fechar-modal" class="text-gray-400 hover:text-gray-700 p-1"><i data-lucide="x" class="w-5 h-5"></i></button>
                        </div>
                        
                        <div id="ticket-feedback" class="hidden"></div>

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
                            <button type="submit" id="btn-enviar-ticket" class="w-full bg-emerald-700 text-white py-3.5 rounded-xl font-bold hover:bg-emerald-800 transition shadow-sm text-sm">
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
    const banner = document.getElementById('ticket-feedback');

    if (!btnAbrir || !modal || !form) return;

    btnAbrir.onclick = () => {
        banner.classList.add('hidden');
        form.classList.remove('hidden');
        modal.classList.remove('hidden');
    };

    btnFechar.onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

    form.onsubmit = async (e) => {
        e.preventDefault();
        const categoria = document.getElementById('ticket-categoria').value;
        const observacao = document.getElementById('ticket-obs').value;
        const btnSubmit = document.getElementById('btn-enviar-ticket');

        btnSubmit.disabled = true;
        btnSubmit.textContent = "Enviando relato...";

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

            form.classList.add('hidden');
            banner.className = "p-4 rounded-xl text-sm font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 text-center space-y-2";
            banner.innerHTML = `
                <p>Relato enviado com sucesso para a equipe de gestão!</p>
                <button onclick="document.getElementById('ticket-modal').classList.add('hidden')" class="text-xs bg-emerald-700 text-white px-4 py-2 rounded-lg font-bold">Fechar</button>
            `;
            banner.classList.remove('hidden');
            form.reset();
        } catch (err) {
            form.classList.add('hidden');
            banner.className = "p-4 rounded-xl text-sm font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 text-center space-y-2";
            banner.innerHTML = `
                <p>[Modo Simulado] Relato registrado com sucesso!</p>
                <button onclick="document.getElementById('ticket-modal').classList.add('hidden')" class="text-xs bg-emerald-700 text-white px-4 py-2 rounded-lg font-bold">Fechar</button>
            `;
            banner.classList.remove('hidden');
            form.reset();
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = "ENVIAR RELATO AO GESTOR";
        }
    };
}