export async function renderPainelOperador() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-700"></div></div>`;

    try {
        const [maquinasRes, climaRes] = await Promise.all([
            fetch('/maquinas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }),
            fetch('/clima/operador', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(res => res.ok ? res.json() : null).catch(() => null)
        ]);

        const minhasMaquinas = maquinasRes.ok ? await maquinasRes.json() : [];

        if (!minhasMaquinas || minhasMaquinas.length === 0) {
            container.innerHTML = `
                <div class="text-center py-16 space-y-3">
                    <i data-lucide="tractor" class="w-16 h-16 mx-auto text-gray-300"></i>
                    <h3 class="text-lg font-bold text-gray-800">Nenhum equipamento vinculado</h3>
                    <p class="text-sm text-gray-500 max-w-sm mx-auto">Entre em contato com seu gestor para vincular máquinas ao seu perfil operacional.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        const clima = climaRes || { previsao: [], tem_alerta: false };
        const regiaoNome = minhasMaquinas[0]?.fazenda_nome || minhasMaquinas[0]?.cidade || 'Sua Região';

        container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500 max-w-3xl mx-auto">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Painel Operacional</h3>
                    <p class="text-gray-500 text-sm">Monitore os ativos sob sua responsabilidade e reporte ocorrências no campo.</p>
                </div>

                <!-- Lista de Cards (Exibe todas as máquinas vinculadas) -->
                <div class="space-y-6">
                    ${minhasMaquinas.map(maquina => {
            const classificacao = maquina.classificacao || 'BAIXO';
            const statusConfig = {
                'ALTO': {
                    bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'alert-octagon',
                    titulo: 'Atenção: Verifique antes de operar',
                    msg: 'O sistema detectou indicadores elevados de risco neste equipamento. Faça uma inspeção visual.'
                },
                'MEDIO': {
                    bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: 'alert-triangle',
                    titulo: 'Cautela recomendada na operação',
                    msg: 'Condições ambientais exigem maior atenção durante o trabalho.'
                },
                'BAIXO': {
                    bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: 'check-circle',
                    titulo: 'Pronto para uso seguro',
                    msg: 'Parâmetros operacionais e climáticos normais.'
                }
            }[classificacao] || {
                bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', icon: 'info',
                titulo: 'Status Regular',
                msg: 'Equipamento monitorado sem alertas críticos.'
            };

            const eqpId = maquina.equipamento_id || maquina.EQUIPAMENTO_ID;

            return `
                            <div class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-6 hover:border-emerald-500 transition">
                                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-gray-100 pb-6">
                                    <div>
                                        <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Ativo Atribuído</span>
                                        <div class="text-3xl font-black text-gray-900 mt-1">${eqpId}</div>
                                        <p class="text-xs text-gray-500 mt-1">Propriedade: <span class="font-semibold text-gray-800">${maquina.fazenda_nome || 'Área Rural'}</span></p>
                                    </div>
                                    <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                                        <button data-eqp="${eqpId}" class="btn-reportar bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-bold hover:bg-emerald-800 transition shadow-sm text-xs flex items-center gap-1.5">
                                            <i data-lucide="message-square-warning" class="w-4 h-4"></i> Reportar Problema
                                        </button>
                                        <a href="#detalhe?eqp=${eqpId}" class="bg-gray-100 text-gray-800 px-4 py-2.5 rounded-xl font-bold hover:bg-gray-200 transition text-xs">
                                            Ver Detalhes →
                                        </a>
                                    </div>
                                </div>

                                <div class="${statusConfig.bg} border ${statusConfig.border} p-5 rounded-xl flex items-start gap-4">
                                    <i data-lucide="${statusConfig.icon}" class="w-7 h-7 ${statusConfig.text} shrink-0 mt-0.5"></i>
                                    <div class="space-y-1">
                                        <h4 class="text-sm font-extrabold ${statusConfig.text}">${statusConfig.titulo}</h4>
                                        <p class="text-xs text-gray-700 leading-relaxed">${statusConfig.msg}</p>
                                    </div>
                                </div>
                            </div>
                        `;
        }).join('')}
                </div>

                <!-- Card de Previsão do Tempo -->
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

                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                        ${!clima.previsao || clima.previsao.length === 0 ? `
                            <p class="col-span-4 text-xs text-gray-400 italic text-center py-4">Dados meteorológicos indisponíveis no momento.</p>
                        ` : clima.previsao.slice(0, 4).map(p => {
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
                    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
                        <div class="flex justify-between items-center border-b pb-3">
                            <div>
                                <h4 class="font-extrabold text-gray-900 text-lg">Reportar Problema</h4>
                                <p class="text-xs text-gray-500" id="modal-eqp-label">Máquina: ---</p>
                            </div>
                            <button id="btn-fechar-modal" class="text-gray-400 hover:text-gray-700 p-1"><i data-lucide="x" class="w-5 h-5"></i></button>
                        </div>
                        
                        <div id="ticket-feedback" class="hidden"></div>

                        <form id="ticket-form" class="space-y-4">
                            <input type="hidden" id="ticket-eqp-input">
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

        // Vinculação correta dos eventos diretamente no DOM recém-criado
        configurarEventosOperador();

    } catch (error) {
        container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar painel do operador.</p>`;
    }
}

function configurarEventosOperador() {
    const modal = document.getElementById('ticket-modal');
    const btnFechar = document.getElementById('btn-fechar-modal');
    const form = document.getElementById('ticket-form');
    const banner = document.getElementById('ticket-feedback');

    // Botões de reportar problema de cada máquina
    document.querySelectorAll('.btn-reportar').forEach(btn => {
        btn.onclick = () => {
            const eqpId = btn.getAttribute('data-eqp');
            document.getElementById('modal-eqp-label').textContent = `Máquina: ${eqpId}`;
            document.getElementById('ticket-eqp-input').value = eqpId;

            banner.classList.add('hidden');
            form.classList.remove('hidden');
            modal.classList.remove('hidden');
        };
    });

    if (btnFechar) btnFechar.onclick = () => modal.classList.add('hidden');
    if (modal) modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            const equipamentoId = document.getElementById('ticket-eqp-input').value;
            const categoria = document.getElementById('ticket-categoria').value;
            const observacao = document.getElementById('ticket-obs').value;
            const btnSubmit = document.getElementById('btn-enviar-ticket');
            const banner = document.getElementById('ticket-feedback');

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

                if (!response.ok) {
                    const errJson = await response.json().catch(() => ({}));
                    throw new Error(errJson.detail || "Erro ao enviar ticket.");
                }

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
                banner.className = "p-4 rounded-xl text-sm font-bold bg-red-50 text-red-800 border border-red-200 text-center space-y-2";
                banner.innerHTML = `
                    <p>${err.message || "Erro ao conectar com o servidor."}</p>
                    <button onclick="document.getElementById('ticket-modal').classList.add('hidden')" class="text-xs bg-red-700 text-white px-4 py-2 rounded-lg font-bold">Fechar</button>
                `;
                banner.classList.remove('hidden');
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.textContent = "ENVIAR RELATO AO GESTOR";
            }
        };
    }
}