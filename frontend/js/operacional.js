import { fetchHistorico } from './api.js';

export async function renderOperacional() {
    const container = document.getElementById('view-content');
    container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

    const data = await fetchHistorico();
    if (data.length === 0) return;

    const alto = data.filter(d => d.CLASSIFICACAO === 'ALTO').length;
    const medio = data.filter(d => d.CLASSIFICACAO === 'MEDIO').length;
    const totalEqp = new Set(data.map(d => d.EQUIPAMENTO_ID)).size;

    container.innerHTML = `
        <div class="space-y-8 animate-in fade-in duration-500">
            <div class="border-b pb-4">
                <h3 class="text-2xl font-bold text-gray-900">Status Operacional da Frota</h3>
                <p class="text-gray-500">Visão geográfica e métricas de severidade em tempo real.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-red-50 border-l-4 border-[#D92D20] p-6 rounded-r-xl">
                    <span class="text-xs font-bold text-[#B42318] uppercase">Risco Crítico</span>
                    <div class="text-4xl font-black text-[#D92D20]">${alto}</div>
                </div>
                <div class="bg-amber-50 border-l-4 border-[#FDB022] p-6 rounded-r-xl">
                    <span class="text-xs font-bold text-[#DC6803] uppercase">Atenção</span>
                    <div class="text-4xl font-black text-[#DC6803]">${medio}</div>
                </div>
                <div class="bg-gray-50 border-l-4 border-gray-400 p-6 rounded-r-xl">
                    <span class="text-xs font-bold text-gray-600 uppercase">Equipamentos Ativos</span>
                    <div class="text-4xl font-black text-gray-900">${totalEqp}</div>
                </div>
            </div>

            <div class="space-y-4">
                <h4 class="font-bold text-gray-700 flex items-center gap-2">
                    <i data-lucide="map-pin" class="w-4 h-4"></i> Localização de Incidentes Críticos
                </h4>
                <div id="map" class="w-full h-[500px] rounded-2xl border border-gray-200 z-10"></div>
            </div>
        </div>
    `;

    lucide.createIcons();

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            initMap(data.filter(d => d.CLASSIFICACAO === 'ALTO'));
        });
    });


}

function initMap(pontosCriticos) {
    const map = L.map('map').setView([-22.5, -47.5], 7);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    const coords_base = {
        "São Paulo": [-23.55, -46.63], "Campinas": [-22.90, -47.06],
        "Ribeirão Preto": [-21.17, -47.81], "Sorocaba": [-23.50, -47.45],
        "Piracicaba": [-22.73, -47.64]
    };

    pontosCriticos.forEach(p => {
        const base = coords_base[p.CIDADE] || [-23.5, -46.6];
        const lat = base[0] + (Math.random() - 0.5) * 0.05;
        const lon = base[1] + (Math.random() - 0.5) * 0.05;

        L.circleMarker([lat, lon], {
            radius: 6,
            fillColor: "#DF082A",
            color: "#FFFFFF",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup(`<b>${p.EQUIPAMENTO_ID}</b><br>Score: ${(p.PROBABILIDADE_ALTO * 100).toFixed(1)}%`);
    });
}