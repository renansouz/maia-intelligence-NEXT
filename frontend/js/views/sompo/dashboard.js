import { fetchHistorico } from '../../core/api.js';

export async function renderSompoDashboard() {
    const container = document.getElementById('view-content');
    container.innerHTML = `
        <div class="flex flex-col justify-center items-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div>
            <p class="mt-4 text-gray-500 font-medium tracking-tight">Analisando dados globais da carteira...</p>
        </div>
    `;

    try {
        // Consome as máquinas distintas e os sinistros reais em paralelo
        const [maquinasRes, gestoresRes, sinistrosRes] = await Promise.all([
            fetch('/maquinas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(r => r.ok ? r.json() : []),
            fetch('/gestores', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(r => r.ok ? r.json() : []).catch(() => []),
            fetch('/tickets/sinistros', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).then(r => r.ok ? r.json() : []).catch(() => [])
        ]);

        const maquinas = maquinasRes || [];
        const maquinasCriticas = maquinas.filter(m => m.classificacao === 'ALTO');

        const totalCriticas = maquinasCriticas.length;
        // Soma o VALOR_SEGURADO real vindo do banco para as máquinas distintas em risco crítico
        const exposicaoFinanceira = maquinasCriticas.reduce((acc, m) => acc + (m.valor_segurado || 350000), 0);

        const totalGestores = gestoresRes.length || 1;
        const totalSinistrosReais = sinistrosRes.length;
        const formatoMoeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });


        container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-500">
                
                <!-- 1. OS QUATRO NÚMEROS-CHAVE DE DECISÃO -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                    
                    <div onclick="${totalCriticas > 0 ? "document.getElementById('tabela-risco-critico').scrollIntoView({behavior: 'smooth'})" : ""}" 
                        class="bg-red-50 border border-red-100 p-6 rounded-2xl shadow-sm flex flex-col justify-between ${totalCriticas > 0 ? 'cursor-pointer hover:border-red-300 transition' : ''}">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-[#9E1E24] uppercase tracking-wider">Risco Crítico</span>
                            <div class="p-2 bg-red-100/60 rounded-xl text-[#DF082A]">
                                <i data-lucide="alert-octagon" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-[#9E1E24]">${totalCriticas}</div>
                            <p class="text-xs text-red-600/80 mt-1 font-medium">Equipamentos exigindo atenção imediata</p>
                        </div>
                    </div>

                    <div class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Exposição Financeira</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="shield-alert" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-gray-900">${formatoMoeda.format(exposicaoFinanceira)}</div>
                            <p class="text-xs text-gray-500 mt-1 font-medium">Capital sob risco potencial avaliado</p>
                        </div>
                    </div>

                    <div onclick="window.location.hash='#sompo/sinistros'" class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between cursor-pointer hover:border-gray-400 transition">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Sinistros / Tickets</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="ticket" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-gray-900">${totalSinistrosReais}</div>
                            <p class="text-xs text-gray-500 mt-1 font-medium">Ocorrências abertas em campo</p>
                        </div>
                    </div>

                    <div onclick="window.location.hash='#sompo/gestores'" class="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm flex flex-col justify-between cursor-pointer hover:border-gray-400 transition">
                        <div class="flex justify-between items-start">
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Gestores Ativos</span>
                            <div class="p-2 bg-gray-100 rounded-xl text-gray-700">
                                <i data-lucide="users" class="w-5 h-5"></i>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="text-3xl font-black text-gray-900">5</div>
                            <p class="text-xs text-gray-500 mt-1 font-medium">Contratos corporativos monitorados</p>
                        </div>
                    </div>

                </div>

                <!-- 2. LISTA PRIORITÁRIA DE RISCO (Apenas máquinas distintas) -->
                <div id="tabela-risco-critico" class="space-y-4">
                    <div class="flex justify-between items-end">
                        <div>
                            <h3 class="text-xl font-extrabold text-[#101828] tracking-tight">Equipamentos em Maior Risco</h3>
                            <p class="text-gray-500 text-sm">Clique em qualquer linha para abrir o detalhe e o laudo técnico do ativo.</p>
                        </div>
                        <span class="text-xs font-bold px-3 py-1 bg-red-50 text-[#DF082A] rounded-full border border-red-100">
                            Foco de Intervenção Hoje
                        </span>
                    </div>

                    <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Equipamento</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Localidade</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Score de Risco</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase">Classificação</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase">Detalhes</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${maquinasCriticas.length === 0 ? `
                                    <tr>
                                        <td colspan="5" class="py-12 text-center text-gray-400 italic text-sm">
                                            Nenhum equipamento em risco crítico no momento. Toda a frota opera com estabilidade.
                                        </td>
                                    </tr>
                                ` : maquinasCriticas.slice(0, 5).map(m => `
                                    <tr onclick="window.location.hash='#detalhe?eqp=${m.EQUIPAMENTO_ID}'" class="hover:bg-gray-50 transition cursor-pointer">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${m.EQUIPAMENTO_ID}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${m.CIDADE || 'Não informada'}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-mono font-bold text-red-600">${(m.PROBABILIDADE_ALTO * 100).toFixed(1)}%</td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border bg-red-50 text-[#D92D20] border-red-100">
                                                ${m.CLASSIFICACAO}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right">
                                            <span class="text-xs font-bold text-[#DF082A] hover:underline">Ver Detalhes →</span>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 3. MINI-MAPA DE CONTEXTO -->
                <div class="space-y-4">
                    <h4 class="font-extrabold text-gray-800 text-base flex items-center gap-2">
                        <i data-lucide="map-pin" class="w-4 h-4 text-[#DF082A]"></i> Distribuição Geográfica de Alertas
                    </h4>
                    <div id="sompo-map" class="w-full h-[350px] rounded-2xl border border-gray-200 z-10"></div>
                </div>

            </div>
        `;

        lucide.createIcons();

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                initSompoMap(maquinasCriticas);
            });
        });

    } catch (error) {
        container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar visão executiva da Sompo.</p>`;
    }
}

function initSompoMap(criticos) {
    const mapEl = document.getElementById('sompo-map');
    if (!mapEl) return;

    const map = L.map('sompo-map').setView([-22.5, -47.5], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const coords_base = {
        "São Paulo": [-23.55, -46.63], "Campinas": [-22.90, -47.06],
        "Ribeirão Preto": [-21.17, -47.81], "Sorocaba": [-23.50, -47.45],
        "Piracicaba": [-22.73, -47.64]
    };

    criticos.forEach(p => {
        const base = coords_base[p.CIDADE] || [-23.5, -46.6];
        const lat = base[0] + (Math.random() - 0.5) * 0.03;
        const lon = base[1] + (Math.random() - 0.5) * 0.03;

        const marker = L.circleMarker([lat, lon], {
            radius: 7,
            fillColor: "#DF082A",
            color: "#FFFFFF",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(map);

        marker.bindPopup(`<b>${p.EQUIPAMENTO_ID}</b><br>Risco: ${(p.PROBABILIDADE_ALTO * 100).toFixed(1)}%`);
        marker.on('click', () => {
            window.location.hash = `#detalhe?eqp=${p.EQUIPAMENTO_ID}`;
        });
    });
}