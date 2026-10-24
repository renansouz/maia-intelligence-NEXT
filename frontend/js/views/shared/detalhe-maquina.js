import { getPapel } from '../../core/auth.js';

export async function renderDetalheMaquina() {
    const container = document.getElementById('view-content');

    const hashParts = window.location.hash.split('?');
    const params = new URLSearchParams(hashParts[1] || '');
    const equipamentoId = params.get('eqp');

    if (!equipamentoId) {
        container.innerHTML = `
            <div class="text-center py-16 space-y-3">
                <i data-lucide="alert-circle" class="w-12 h-12 mx-auto text-amber-500"></i>
                <h3 class="text-lg font-bold text-gray-800">Nenhum equipamento selecionado</h3>
                <p class="text-sm text-gray-500">Retorne à listagem anterior e selecione um ativo para inspecionar.</p>
                <div class="pt-4"><a href="javascript:history.back()" class="text-xs font-bold bg-gray-900 text-white px-4 py-2 rounded-lg">Voltar</a></div>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div></div>`;
    // Atualização assíncrona do card ambiental para simular requisição orbital em tempo real

    try {
        const [detalheRes, historicoRes] = await Promise.all([
            fetch(`/maquinas/${equipamentoId}/detalhe`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
            }),
            fetch(`/maquinas/${equipamentoId}/historico`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
            })
        ]);

        if (!detalheRes.ok) {
            const errJson = await detalheRes.json().catch(() => ({}));
            throw new Error(errJson.detail || `Erro na API (${detalheRes.status})`);
        }

        const maquina = await detalheRes.json();
        const historico = historicoRes.ok ? await historicoRes.json() : [];
        const papel = getPapel();
        const isOperador = papel === 'OPERADOR';

        const diag = maquina.diagnostico || {};
        const classificacao = diag.classificacao || 'BAIXO';

        // Garante a conversão correta do score para porcentagem (0 a 100)
        let rawScore = typeof diag.score === 'number' ? diag.score : 0;
        const scorePercentual = rawScore <= 1 ? rawScore * 100 : rawScore;

        const explicacaoCompleta = diag.explicacao_completa || 'RESUMO: Equipamento em condições estáveis de operação. || FATORES: Nenhum fator crítico detectado.';
        const hashAuditoria = diag.hash_auditoria || 'N/D';

        const configRisco = {
            'ALTO': { color: '#D92D20', bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'bg-red-50 text-red-700 border-red-200' },
            'MEDIO': { color: '#FDB022', bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-50 text-amber-700 border-amber-200' },
            'BAIXO': { color: '#12B76A', bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
        }[classificacao] || { color: '#475467', bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', badge: 'bg-gray-50 text-gray-700 border-gray-200' };

        const partes = explicacaoCompleta.split(' || ');
        const listaFatores = partes.find(p => p && p.includes('FATORES:'))?.replace('FATORES:', '').split(',') || [];

        container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
                
                <!-- Cabeçalho -->
                <div class="border-b border-gray-100 pb-4 flex justify-between items-center">
                    <div>
                        <div class="flex items-center gap-3">
                            <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">${maquina.equipamento_id}</h3>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${configRisco.badge}">${classificacao}</span>
                        </div>
                        <p class="text-gray-500 text-sm mt-0.5">${maquina.tipo || 'Equipamento'} · ${maquina.modelo || 'Modelo não especificado'} (${maquina.ano || 'Ano N/D'})</p>
                    </div>
                    <button onclick="history.back()" class="text-xs font-bold text-gray-600 hover:text-black bg-white border border-gray-200 px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-1.5">
                        <i data-lucide="arrow-left" class="w-4 h-4"></i> Voltar
                    </button>
                </div>

                <!-- Grid Principal -->
                <div class="grid grid-cols-1 ${isOperador ? 'max-w-2xl mx-auto' : 'lg:grid-cols-3'} gap-8 items-start">
                    
                    <!-- Coluna da Esquerda / Centro: XAI & Histórico -->
                    <div class="${isOperador ? 'col-span-1' : 'lg:col-span-2'} space-y-6">
                        
                        <!-- Bloco XAI Reestruturado & Indicadores Ambientais -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            <!-- Gráfico Gauge Operacional -->
                            <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm flex flex-col items-center justify-between">
                                <h4 class="text-sm font-bold text-[#344054] self-start mb-2">Saúde Operacional (CAN)</h4>
                                <div id="gauge-chart" class="w-full h-[180px]"></div>
                                <div class="text-center mt-2">
                                    <span class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Status Mecânico</span>
                                    <div class="text-lg font-black" style="color: ${configRisco.color}">${classificacao}</div>
                                </div>
                            </div>

                            <!-- Indicador Ambiental Focado em Segurança no Campo -->
                            <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                                <h4 class="text-sm font-bold text-[#344054] self-start mb-4">Condição do Solo e do Terreno</h4>
                                ${maquina.ambiental ? (() => {
                const cfg = {
                    'muito_proxima_do_padrao': { icon: 'check-circle', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', title: 'Condição Estável e Segura', desc: 'Terreno firme, operando na normalidade.' },
                    'proxima_do_padrao': { icon: 'check-circle', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', title: 'Condição Segura', desc: 'Sem indícios críticos de umidade excessiva.' },
                    'afastada_do_padrao': { icon: 'alert-triangle', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', title: 'Atenção: Solo Instável', desc: 'Evite áreas baixas ou margens de rios.' },
                    'muito_afastada_do_padrao': { icon: 'alert-octagon', color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200', title: 'Crítico: Risco de Atolamento', desc: 'Solo saturado. Recomenda-se suspender operação no talhão.' }
                }[maquina.ambiental.faixa_condicao] || { icon: 'info', color: 'text-blue-900', bg: 'bg-blue-50', border: 'border-blue-200', title: 'Condição Regular', desc: 'Monitoramento em andamento.' };

                return `
                                    <div class="${cfg.bg} border ${cfg.border} p-5 rounded-xl flex items-start gap-4 my-auto animate-in fade-in duration-300">
                                        <i data-lucide="${cfg.icon}" class="w-6 h-6 ${cfg.color} shrink-0 mt-0.5"></i>
                                        <div class="space-y-1">
                                            <h5 class="text-sm font-black ${cfg.color}">${cfg.title}</h5>
                                            <p class="text-xs text-gray-700 leading-relaxed">${cfg.desc}</p>
                                            <div class="text-[9px] text-gray-400 font-mono pt-1">Índice orbital: ${maquina.ambiental.score_ambiental}%</div>
                                        </div>
                                    </div>
                                `;
            })() : `
                                    <div class="text-center py-10 text-gray-400 text-xs italic bg-gray-50 rounded-xl border border-dashed border-gray-200 my-auto">
                                        Dados de solo indisponíveis para esta localidade.
                                    </div>
                                `}
                                <p class="text-[10px] text-gray-400 text-center mt-4">Monitoramento satelital de umidade e relevo</p>
                            </div>

                        </div>

                        <!-- Fatores de Influência (SHAP) -->
                        <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Fatores de Influência Operacional (SHAP)</h4>
                            <div class="space-y-3">
                                ${listaFatores.length > 0 && listaFatores[0].trim() !== "" ? listaFatores.map(f => `
                                    <div class="flex items-center gap-3 text-xs font-semibold text-[#101828] bg-gray-50 p-3 rounded-xl border border-gray-100">
                                        <div class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: ${configRisco.color}"></div>
                                        <span class="capitalize">${f.trim()}</span>
                                    </div>
                                `).join('') : `
                                    <div class="text-center py-6 text-gray-400 text-xs italic bg-gray-50 rounded-xl border border-dashed border-gray-200">
                                        Nenhum fator crítico predominante detectado.
                                    </div>
                                `}
                            </div>
                        </div>


                        <!-- Bloco de Auditoria -->
                        ${!isOperador ? `
                            <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm space-y-3">
                                <div class="flex items-center gap-2 text-[#027A48]">
                                    <i data-lucide="shield-check" class="w-4 h-4"></i>
                                    <span class="text-xs font-extrabold uppercase tracking-wider">Registro de Auditoria Verificado</span>
                                </div>
                                <p class="text-xs text-gray-500 leading-relaxed">
                                    Este laudo foi processado e encadeado matematicamente ao histórico da frota. A assinatura digital abaixo garante a imutabilidade desta decisão.
                                </p>
                                <div class="bg-[#F2F4F7] p-2.5 rounded-lg font-mono text-[10px] text-[#344054] border border-[#EAECF0] break-all select-all">
                                    ${hashAuditoria}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Histórico de Ocorrências -->
                        <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest">Histórico de Ocorrências e Manutenções</h4>
                            
                            ${historico.length === 0 ? `
                                <p class="text-xs text-gray-400 italic py-6 text-center">Nenhum evento registrado no histórico deste equipamento.</p>
                            ` : `
                                <div class="space-y-4 pt-2">
                                    ${(isOperador ? historico.slice(0, 3) : historico).map(ev => `
                                        <div class="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                                            <div class="p-2 rounded-lg ${ev.tipo_evento === 'TICKET' ? 'bg-amber-50 text-amber-700' : 'bg-blue-50 text-blue-900'}">
                                                <i data-lucide="${ev.tipo_evento === 'TICKET' ? 'message-square-warning' : 'wrench'}" class="w-4 h-4"></i>
                                            </div>
                                            <div class="flex-1">
                                                <div class="flex justify-between items-center">
                                                    <span class="text-xs font-bold text-gray-900">${ev.titulo}</span>
                                                    <span class="text-[10px] text-gray-400">${new Date(ev.data).toLocaleDateString('pt-BR')}</span>
                                                </div>
                                                <p class="text-xs text-gray-600 mt-1">${ev.detalhe || 'Sem observações.'}</p>
                                                <div class="flex gap-4 mt-2 text-[10px] text-gray-500 font-medium">
                                                    <span>Status: <strong class="text-gray-700">${ev.status}</strong></span>
                                                    ${ev.responsavel ? `<span>Responsável: <strong class="text-gray-700">${ev.responsavel}</strong></span>` : ''}
                                                </div>
                                                ${ev.antes_depois ? renderAntesDepois(ev.antes_depois) : ''}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            `}
                        </div>

                    </div>

                    <!-- Coluna da Direita: Localidade e Ações -->
                    <div class="space-y-6">
                        
                        ${!isOperador ? `
                            <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest">Localidade</h4>
                                <div>
                                    <div class="text-sm font-bold text-gray-900">${maquina.fazenda_nome || 'Fazenda não vinculada'}</div>
                                    <p class="text-xs text-gray-500 mt-0.5">${maquina.endereco || 'Endereço não informado'}</p>
                                </div>
                                <div class="pt-3 border-t border-gray-100">
                                    <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Gestor Responsável</span>
                                    <div class="text-xs font-semibold text-gray-800 mt-0.5">${maquina.gestor_nome || 'N/D'}</div>
                                    <div class="text-[11px] text-gray-500">${maquina.gestor_email || ''}</div>
                                </div>
                            </div>

                            <div class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-3">
                                <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest">Operadores Atribuídos</h4>
                                ${!maquina.operadores || maquina.operadores.length === 0 ? `
                                    <p class="text-xs text-gray-400 italic">Nenhum operador vinculado a esta máquina.</p>
                                ` : maquina.operadores.map(op => `
                                    <div class="text-xs bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                                        <div class="font-bold text-gray-900">${op.nome}</div>
                                        <div class="text-gray-500 text-[11px]">${op.email}</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}

                        ${papel === 'GESTOR' ? `
                            <button id="btn-solicitar-manutencao" class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition shadow-sm text-xs flex items-center justify-center gap-2">
                                <i data-lucide="wrench" class="w-4 h-4"></i> Solicitar Manutenção
                            </button>
                        ` : ''}

                    </div>

                </div>

                <!-- Modal de Solicitação de Manutenção -->
                <div id="manutencao-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
                        <div class="flex justify-between items-center border-b pb-3">
                            <h4 class="font-extrabold text-gray-900 text-base">Solicitar Manutenção Externa</h4>
                            <button id="fechar-modal-manut" class="text-gray-400 hover:text-gray-700"><i data-lucide="x" class="w-5 h-5"></i></button>
                        </div>
                        
                        <div id="modal-corpo-form" class="space-y-4">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Descrição do Problema / Motivo</label>
                                <textarea id="manut-desc" required rows="3" placeholder="Ex: Relato de superaquecimento e ruído no motor..."
                                    class="w-full bg-white border border-gray-300 rounded-lg p-3 text-sm outline-none focus:ring-2 focus:ring-blue-900 resize-none"></textarea>
                            </div>
                            <button id="btn-enviar-manut" class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                                GERAR LINK ÚNICO PARA O TÉCNICO
                            </button>
                        </div>

                        <div id="modal-corpo-sucesso" class="hidden space-y-4 text-center py-2">
                            <div class="bg-emerald-50 p-3 rounded-full w-12 h-12 mx-auto flex items-center justify-center text-emerald-700">
                                <i data-lucide="check" class="w-6 h-6"></i>
                            </div>
                            <h5 class="font-bold text-gray-900">Link Gerado com Sucesso!</h5>
                            <p class="text-xs text-gray-500">Copie a mensagem abaixo e envie para o técnico de manutenção:</p>
                            <div id="mensagem-copia" class="bg-gray-50 p-3 rounded-xl border text-xs text-left font-mono text-gray-700 select-all break-all max-h-32 overflow-y-auto"></div>
                            <button id="btn-copiar-msg" class="w-full bg-emerald-700 text-white py-3 rounded-xl font-bold hover:bg-emerald-800 transition text-sm flex items-center justify-center gap-2">
                                <i data-lucide="copy" class="w-4 h-4"></i> Copiar Mensagem
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        `;

        lucide.createIcons();

        requestAnimationFrame(() => {
            renderGauge(scorePercentual, configRisco.color);
        });

        if (papel === 'GESTOR') {
            const modal = document.getElementById('manutencao-modal');
            const btnAbrir = document.getElementById('btn-solicitar-manutencao');
            const btnFechar = document.getElementById('fechar-modal-manut');
            const btnEnviar = document.getElementById('btn-enviar-manut');
            const btnCopiar = document.getElementById('btn-copiar-msg');

            btnAbrir.onclick = () => modal.classList.remove('hidden');
            btnFechar.onclick = () => modal.classList.add('hidden');
            modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };

            btnEnviar.onclick = async () => {
                const descInput = document.getElementById('manut-desc');
                const desc = descInput.value.trim();
                if (!desc) {
                    descInput.classList.add('border-red-500', 'ring-2', 'ring-red-200');
                    return;
                }

                btnEnviar.disabled = true;
                btnEnviar.textContent = "Gerando link...";

                try {
                    const res = await fetch('/manutencao/solicitar', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
                        },
                        body: JSON.stringify({ equipamento_id: equipamentoId, descricao: desc, tipo: "PREVENTIVA" })
                    });

                    if (!res.ok) {
                        const errJson = await res.json().catch(() => ({}));
                        throw new Error(errJson.detail || "Erro ao gerar solicitação.");
                    }
                    const data = await res.json();

                    const linkTecnico = `${window.location.origin}/manutencao.html?token=${data.token}`;
                    const textoPronto = `Olá! Muito obrigado por cuidar da manutenção do nosso equipamento ${equipamentoId} 🙏 Poderia preencher este formulário rápido (leva menos de 2 minutos) para atualizarmos nosso sistema? ${linkTecnico}. Agradecemos demais pelo trabalho!`;

                    document.getElementById('modal-corpo-form').classList.add('hidden');
                    document.getElementById('mensagem-copia').textContent = textoPronto;
                    document.getElementById('modal-corpo-sucesso').classList.remove('hidden');
                    lucide.createIcons();

                } catch (err) {
                    alert(err.message);
                    btnEnviar.disabled = false;
                    btnEnviar.textContent = "GERAR LINK ÚNICO PARA O TÉCNICO";
                }
            };

            btnCopiar.onclick = () => {
                const texto = document.getElementById('mensagem-copia').textContent;
                navigator.clipboard.writeText(texto);
                btnCopiar.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Copiado!`;
                setTimeout(() => {
                    btnCopiar.innerHTML = `<i data-lucide="copy" class="w-4 h-4"></i> Copiar Mensagem`;
                    lucide.createIcons();
                }, 2000);
            };
        }

    } catch (error) {
        console.error("Erro ao carregar detalhes:", error);
        container.innerHTML = `
            <div class="text-center py-16 space-y-3">
                <i data-lucide="alert-triangle" class="w-12 h-12 mx-auto text-red-500"></i>
                <h3 class="text-lg font-bold text-gray-800">Não foi possível carregar os detalhes</h3>
                <p class="text-sm text-red-600 font-medium max-w-md mx-auto">${error.message}</p>
                <div class="pt-4"><a href="javascript:history.back()" class="text-xs font-bold bg-gray-900 text-white px-4 py-2 rounded-lg">Voltar</a></div>
            </div>
        `;
        lucide.createIcons();
    }
}

function renderGauge(score, color) {
    const el = document.getElementById('gauge-chart');
    if (!el) return;
    Plotly.purge(el);

    const data = [{
        type: "indicator",
        mode: "gauge+number",
        value: score,
        number: { suffix: "%", font: { size: 28, family: 'Inter', weight: '800' } },
        gauge: {
            axis: { range: [0, 100], tickwidth: 1, tickcolor: "#D0D5DD" },
            bar: { color: color },
            bgcolor: "white",
            borderwidth: 2,
            bordercolor: "#F2F4F7",
            steps: [
                { range: [0, 30], color: "rgba(18, 183, 106, 0.1)" },
                { range: [30, 70], color: "rgba(253, 176, 34, 0.1)" },
                { range: [70, 100], color: "rgba(217, 45, 32, 0.1)" }
            ],
            threshold: {
                line: { color: "black", width: 4 },
                thickness: 0.75,
                value: score
            }
        }
    }];

    const layout = {
        margin: { t: 10, b: 10, l: 20, r: 20 },
        paper_bgcolor: "rgba(0,0,0,0)",
        font: { family: "Inter, sans-serif" }
    };

    Plotly.newPlot('gauge-chart', data, layout, { staticPlot: true });
}

function renderAntesDepois(ad) {
    const cores = {
        ALTO: 'bg-red-50 text-red-700 border-red-200',
        MEDIO: 'bg-amber-50 text-amber-700 border-amber-200',
        BAIXO: 'bg-emerald-50 text-emerald-700 border-emerald-200'
    };
    const mensagens = {
        AGUARDANDO_TELEMETRIA: 'Manutenção concluída. O risco será reavaliado na próxima telemetria.',
        CONFIRMADA: 'Manutenção confirmada pelos dados: o risco diminuiu.',
        PERSISTE: 'O risco persiste após a manutenção. Recomenda-se nova inspeção.',
        ESTAVEL: 'Sem alteração: a máquina já estava em risco baixo.',
        PIOROU: 'O risco aumentou após a manutenção. Recomenda-se nova inspeção.',
        SEM_COMPARACAO: 'Não há previsão anterior para comparar.'
    };
    const fmt = (iso) => iso
        ? new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
        : '';

    const card = (titulo, p, vazio) => p ? `
        <div class="flex-1 rounded-xl border p-3 ${cores[p.classificacao] || 'bg-gray-50 text-gray-700 border-gray-200'}">
            <div class="text-[9px] font-bold uppercase tracking-widest opacity-70">${titulo}</div>
            <div class="text-sm font-black mt-0.5">${p.classificacao}</div>
            <div class="text-[10px] mt-0.5">Índice de saúde: ${p.saude}</div>
            <div class="text-[9px] opacity-70 mt-1">${fmt(p.data)}</div>
            <div class="text-[9px] font-mono opacity-60">hash …${(p.hash || '').slice(-8)}</div>
        </div>` : `
        <div class="flex-1 rounded-xl border border-dashed border-gray-300 p-3 text-gray-400">
            <div class="text-[9px] font-bold uppercase tracking-widest">${titulo}</div>
            <div class="text-[11px] mt-1 italic">${vazio}</div>
        </div>`;

    return `
        <div class="mt-3 space-y-2">
            <div class="flex items-stretch gap-2">
                ${card('Antes', ad.antes, 'Sem previsão anterior')}
                <div class="self-center text-gray-400 text-sm">→</div>
                ${card('Depois', ad.depois, 'Aguardando telemetria pós-reparo')}
            </div>
            <p class="text-[11px] text-gray-600">${mensagens[ad.estado] || ''}</p>
        </div>`;
}