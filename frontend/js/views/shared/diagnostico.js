import { fetchHistorico, fetchPrevisao } from '../../core/api.js';

let isProcessing = false;

export async function renderDiagnostico() {
  if (isProcessing) return;
  isProcessing = true;

  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    const data = await fetchHistorico();
    const equipamentos = [...new Set(data.map(d => d.EQUIPAMENTO_ID))].sort();

    container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-700">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Diagnóstico Individual XAI</h3>
                    <p class="text-gray-500 text-sm">IA Explicável: Entenda os motivos técnicos por trás de cada score de risco.</p>
                </div>

                <div class="bg-[#F9FAFB] p-8 rounded-2xl border border-[#EAECF0] flex flex-col md:flex-row items-end gap-4">
                    <div class="flex-1">
                        <label class="block text-xs font-bold text-[#475467] uppercase mb-2">Selecione o Equipamento para Laudo</label>
                        <select id="eq-selector" class="w-full bg-white border border-[#D0D5DD] rounded-lg px-4 py-2.5 text-[#101828] focus:ring-2 focus:ring-[#DF082A] outline-none transition">
                            ${equipamentos.map(id => `<option value="${id}">${id}</option>`).join('')}
                        </select>
                    </div>
                    <button id="btn-analisar" class="bg-[#DF082A] text-white px-8 py-2.5 rounded-lg font-bold hover:bg-[#9E1E24] transition-all shadow-md active:scale-95">
                        GERAR LAUDO TÉCNICO
                    </button>
                </div>

                <!-- Área do Resultado (Injetada dinamicamente) -->
                <div id="diagnostico-result" class="min-h-[300px]">
                    <div class="flex flex-col items-center justify-center py-20 opacity-30">
                        <i data-lucide="brain-circuit" class="w-16 h-16 mb-4"></i>
                        <p class="font-medium">Aguardando solicitação de análise...</p>
                    </div>
                </div>
            </div>
        `;

    lucide.createIcons();
    document.getElementById('btn-analisar').addEventListener('click', () => processarAnalise());
    isProcessing = false;

  } catch (error) {
    console.error("Erro ao carregar equipamentos:", error);
    isProcessing = false;
  }
}

async function processarAnalise() {
  const eqId = document.getElementById('eq-selector').value;
  const resultContainer = document.getElementById('diagnostico-result');

  resultContainer.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#DF082A]"></div></div>`;

  const res = await fetchPrevisao(eqId);
  if (!res) {
    resultContainer.innerHTML = `<p class="text-red-500 text-center py-10">Erro ao consultar motor de IA.</p>`;
    return;
  }

  const config = {
    'ALTO': { color: '#D92D20', bg: 'bg-red-50', icon: 'alert-octagon' },
    'MEDIO': { color: '#FDB022', bg: 'bg-amber-50', icon: 'alert-triangle' },
    'BAIXO': { color: '#12B76A', bg: 'bg-green-50', icon: 'check-circle' }
  }[res.classificacao];

  resultContainer.innerHTML = `
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch animate-in slide-in-from-bottom-4 duration-500">
            
            <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm flex flex-col items-center">
                <h4 class="text-sm font-bold text-[#344054] mb-4 self-start">Índice de Risco Calculado</h4>
                <div id="gauge-chart" class="w-full h-[250px]"></div>
                <div class="text-center -mt-5">
                    <span class="text-xs font-bold uppercase tracking-widest text-gray-400">Status da IA</span>
                    <div class="text-2xl font-black" style="color: ${config.color}">${res.classificacao}</div>
                </div>
            </div>

            <div class="space-y-6">
                <div class="${config.bg} border-l-4 p-6 rounded-r-2xl" style="border-color: ${config.color}">
                    <h4 class="text-sm font-bold uppercase mb-4" style="color: ${config.color}">Fatores de Influência (SHAP)</h4>
                    <div id="fatores-list" class="space-y-3">
                    </div>
                </div>

                <div class="bg-white border border-[#EAECF0] rounded-2xl p-6 shadow-sm">
                    <div class="flex items-center gap-3 mb-4 text-[#027A48]">
                        <i data-lucide="shield-check"></i>
                        <span class="text-sm font-extrabold uppercase">Registro de Auditoria Verificado</span>
                    </div>
                    <p class="text-xs text-gray-500 mb-2 leading-relaxed">
                        Este laudo foi processado e encadeado matematicamente ao histórico da frota. 
                        A assinatura digital abaixo garante a imutabilidade desta decisão.
                    </p>
                    <div class="bg-[#F2F4F7] p-3 rounded-lg font-mono text-[10px] break-all border border-[#EAECF0] text-[#344054]">
                        ${res.hash_auditoria}
                    </div>
                </div>
            </div>
        </div>
    `;

  const fatoresContainer = document.getElementById('fatores-list');
  const partes = res.explicacao_completa.split(' || ');
  const listaFatores = partes.find(p => p.includes('FATORES:'))?.replace('FATORES:', '').split(',') || [];

  fatoresContainer.innerHTML = listaFatores.map(f => `
        <div class="flex items-center gap-3 text-sm font-medium text-[#101828]">
            <div class="w-2 h-2 rounded-full" style="background-color: ${config.color}"></div>
            <span class="capitalize">${f.trim()}</span>
        </div>
    `).join('') || '<p class="text-xs opacity-60 italic">Nenhum fator crítico predominante.</p>';

  lucide.createIcons();

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      renderGauge(res.score * 100, config.color);
    });
  });
}

function renderGauge(score, color) {
  const el = document.getElementById('gauge-chart');
  if (!el) return;
  Plotly.purge(el);

  const data = [{
    type: "indicator",
    mode: "gauge+number",
    value: score,
    number: { suffix: "%", font: { size: 40, family: 'Inter', weight: '800' } },
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
    margin: { t: 20, b: 20, l: 30, r: 30 },
    paper_bgcolor: "rgba(0,0,0,0)",
    font: { family: "Inter, sans-serif" }
  };

  Plotly.newPlot('gauge-chart', data, layout, { staticPlot: true });
}