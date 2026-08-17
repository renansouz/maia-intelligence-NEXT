import { fetchHistorico } from './api.js';

let isProcessing = false;

export async function renderGestao() {
  if (isProcessing) return;
  isProcessing = true;

  const container = document.getElementById('view-content');

  container.innerHTML = `
        <div class="flex flex-col justify-center items-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div>
            <p class="mt-4 text-gray-500 font-medium tracking-tight">Consolidando inteligência de frota...</p>
        </div>
    `;

  try {
    const data = await fetchHistorico();
    if (!data || data.length === 0) {
      container.innerHTML = `<p class="text-center py-10">Nenhum dado auditado encontrado.</p>`;
      return;
    }

    container.innerHTML = `
            <div class="space-y-12 animate-in fade-in duration-700">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Gestão Estratégica de Riscos</h3>
                    <p class="text-gray-500">Análise histórica e priorização de segurança baseada no motor MAIA.</p>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
                        <h4 class="font-bold text-[#344054] flex items-center gap-2">
                            <span class="w-2 h-2 bg-[#DF082A] rounded-full"></span> Saúde da Frota
                        </h4>
                        <p class="text-sm text-[#667085] leading-relaxed">
                            Proporção de segurança atual. Atualmente, <span class="font-bold text-[#D92D20]">${((data.filter(d => d.CLASSIFICACAO === 'ALTO').length / data.length) * 100).toFixed(1)}%</span> dos equipamentos monitorados exigem intervenção mecânica ou operacional imediata.
                        </p>
                        <div id="chart-pie" class="w-full h-[350px]"></div>
                    </div>

                    <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
                        <h4 class="font-bold text-[#344054] flex items-center gap-2">
                            <span class="w-2 h-2 bg-[#DF082A] rounded-full"></span> Priorização de Atendimento
                        </h4>
                        <p class="text-sm text-[#667085] leading-relaxed">
                            Ranking de criticidade por ID. Estes equipamentos apresentam as maiores probabilidades acumuladas de risco. Recomendamos auditoria técnica prioritária para o topo desta lista.
                        </p>
                        <div id="chart-rank" class="w-full h-[350px]"></div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-4">
                    <h4 class="font-bold text-[#344054] flex items-center gap-2">
                        <span class="w-2 h-2 bg-[#DF082A] rounded-full"></span> Tendência Histórica de Segurança
                    </h4>
                    <p class="text-sm text-[#667085] leading-relaxed">
                        Acompanhamento do score de risco médio da operação ao longo do tempo. Oscilações bruscas indicam eventos climáticos extremos ou mudanças severas no padrão de uso da frota.
                    </p>
                    <div id="chart-trend" class="w-full h-[400px]"></div>
                </div>
            </div>
        `;

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        renderCharts(data);
        isProcessing = false;
      });
    });

  } catch (error) {
    console.error("Erro na renderização:", error);
    isProcessing = false;
  }
}

function renderCharts(data) {
  ['chart-pie', 'chart-rank', 'chart-trend'].forEach(id => {
    const el = document.getElementById(id);
    if (el) Plotly.purge(el);
  });

  const colors = { alto: '#D92D20', medio: '#FDB022', baixo: '#12B76A' };

  // Grafico Pizza
  const counts = {
    'Risco Crítico': data.filter(d => d.CLASSIFICACAO === 'ALTO').length,
    'Atenção': data.filter(d => d.CLASSIFICACAO === 'MEDIO').length,
    'Operação Segura': data.filter(d => d.CLASSIFICACAO === 'BAIXO').length
  };

  const pieData = [{
    values: Object.values(counts),
    labels: Object.keys(counts),
    type: 'pie',
    hole: .45,
    marker: { colors: [colors.alto, colors.medio, colors.baixo] },
    textinfo: 'percent+label',
    hoverinfo: 'label+value'
  }];

  // Ranking
  const eqGroups = {};
  data.forEach(d => {
    if (!eqGroups[d.EQUIPAMENTO_ID]) eqGroups[d.EQUIPAMENTO_ID] = [];
    eqGroups[d.EQUIPAMENTO_ID].push(d.PROBABILIDADE_ALTO);
  });

  const ranking = Object.entries(eqGroups)
    .map(([id, probs]) => ({ id, media: (probs.reduce((a, b) => a + b, 0) / probs.length) * 100 }))
    .sort((a, b) => b.media - a.media)
    .slice(0, 10);

  const rankData = [{
    x: ranking.map(r => r.media),
    y: ranking.map(r => r.id),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#9E1E24' },
    hovertemplate: 'Probabilidade Média: %{x:.1f}%<extra></extra>'
  }];

  // Tendência 
  const dateGroups = {};
  data.forEach(d => {
    const date = d.DATA_MEDICAO.split('T')[0];
    if (!dateGroups[date]) dateGroups[date] = [];
    dateGroups[date].push(d.PROBABILIDADE_ALTO);
  });

  const trend = Object.entries(dateGroups)
    .map(([date, probs]) => ({ date, media: (probs.reduce((a, b) => a + b, 0) / probs.length) * 100 }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  const trendData = [{
    x: trend.map(t => t.date),
    y: trend.map(t => t.media),
    type: 'scatter',
    mode: 'lines',
    line: { color: '#DF082A', width: 3, shape: 'spline' },
    fill: 'tozeroy',
    fillcolor: 'rgba(223, 8, 42, 0.05)',
    hovertemplate: 'Média Diária: %{y:.1f}%<extra></extra>'
  }];

  const layoutBase = {
    font: { family: 'Inter, sans-serif', size: 11, color: '#475467' },
    margin: { t: 20, b: 40, l: 80, r: 20 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  };

  Plotly.newPlot('chart-pie', pieData, { ...layoutBase, showlegend: false });
  Plotly.newPlot('chart-rank', rankData, { ...layoutBase, xaxis: { title: 'Índice de Probabilidade (%)', gridcolor: '#F2F4F7' }, yaxis: { autorange: 'reversed' } });
  Plotly.newPlot('chart-trend', trendData, { ...layoutBase, xaxis: { gridcolor: '#F2F4F7' }, yaxis: { title: 'Risco Médio da Frota (%)', gridcolor: '#F2F4F7' } });
}