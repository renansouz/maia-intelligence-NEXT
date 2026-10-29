export async function renderseguradoraGestores() {
  const container = document.getElementById('view-content');

  const hashParts = window.location.hash.split('?');
  const params = new URLSearchParams(hashParts[1] || '');
  const gestorId = params.get('id');

  if (gestorId) {
    await renderDetalheGestor(container, gestorId);
  } else {
    await renderListaGestores(container);
  }
}

async function renderListaGestores(container) {
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    const res = await fetch('/gestores', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
    });
    const gestores = res.ok ? await res.json() : [];

    container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <!-- Cabeçalho com botão de Voltar à Central de Risco -->
                <div class="border-b border-gray-100 pb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Gestores de Frota Ativos</h3>
                        <p class="text-gray-500 text-sm">Visão geral dos gestores corporativos, suas fazendas e frotas sob monitoramento.</p>
                    </div>
                    <button onclick="window.location.hash='#seguradora/dashboard'" class="text-xs font-bold text-gray-600 hover:text-black bg-white border border-gray-200 px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-1.5">
                        <i data-lucide="arrow-left" class="w-4 h-4"></i> Voltar à Central de Risco
                    </button>
                </div>

                <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Nome</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Email</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Cobertura</th>
                                    <th class="px-6 py-3 text-center text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Fazendas</th>
                                    <th class="px-6 py-3 text-center text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Máquinas</th>
                                    <th class="px-6 py-3 text-center text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Status</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${gestores.length === 0 ? `
                                    <tr><td colspan="7" class="py-12 text-center text-gray-400 italic text-sm">Nenhum gestor cadastrado no momento.</td></tr>
                                ` : gestores.map(g => `
                                    <tr onclick="window.location.hash='#seguradora/gestores?id=${g.id_usuario}'" class="hover:bg-gray-50 transition cursor-pointer">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${g.nome}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${g.email}</td>
                                        <td class="px-6 py-4 whitespace-nowrap"><span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-900 border border-blue-100">${g.tipo_cobertura || 'BÁSICA'}</span></td>
                                        <td class="px-6 py-4 whitespace-nowrap text-center text-xs font-semibold text-gray-800">${g.total_fazendas || 0}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-center text-xs font-semibold text-gray-800">${g.total_maquinas || 0}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-center"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">ATIVO</span></td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right">
                                            <span class="text-xs font-bold text-[#DF082A] hover:underline">Ver Detalhes →</span>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar lista de gestores.</p>`;
  }
}

async function renderDetalheGestor(container, gestorId) {
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    const res = await fetch(`/gestores/${gestorId}/detalhe`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
    });
    if (!res.ok) throw new Error("Erro ao buscar detalhes do gestor.");
    const data = await res.json();
    const { gestor, fazendas, operadores, maquinas } = data;

    container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <div class="border-b border-gray-100 pb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">${gestor.nome}</h3>
                        <p class="text-gray-500 text-sm">${gestor.email} · Cobertura: <strong class="text-gray-800">${gestor.tipo_cobertura || 'Básica'}</strong></p>
                    </div>
                    <button onclick="window.location.hash='#seguradora/gestores'" class="text-xs font-bold text-gray-600 hover:text-black bg-white border border-gray-200 px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-1.5">
                        <i data-lucide="arrow-left" class="w-4 h-4"></i> Voltar à Lista
                    </button>
                </div>

                <!-- Fazendas do Gestor -->
                <div class="space-y-4">
                    <h4 class="text-base font-extrabold text-gray-900">Propriedades Rurais (${fazendas.length})</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${fazendas.length === 0 ? `<p class="text-xs text-gray-400 italic">Nenhuma fazenda cadastrada.</p>` : fazendas.map(f => `
                            <div class="bg-white border border-gray-200 p-4 rounded-xl shadow-sm">
                                <div class="font-bold text-gray-900">${f.nome}</div>
                                <div class="text-xs text-gray-500 mt-1">${f.endereco || 'Endereço não informado'}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Operadores do Gestor -->
                <div class="space-y-4">
                    <h4 class="text-base font-extrabold text-gray-900">Operadores Vinculados (${operadores.length})</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${operadores.length === 0 ? `<p class="text-xs text-gray-400 italic">Nenhum operador cadastrado.</p>` : operadores.map(op => `
                            <div class="bg-white border border-gray-200 p-4 rounded-xl shadow-sm">
                                <div class="font-bold text-gray-900">${op.nome}</div>
                                <div class="text-xs text-gray-500 mt-1">${op.email}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Máquinas da Frota do Gestor -->
                <div class="space-y-4">
                    <h4 class="text-base font-extrabold text-gray-900">Frota de Máquinas (${maquinas.length})</h4>
                    <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Equipamento</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Tipo / Modelo</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Fazenda</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Classificação</th>
                                        <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Score</th>
                                        <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-100">
                                    ${maquinas.length === 0 ? `
                                        <tr><td colspan="6" class="py-8 text-center text-gray-400 italic text-sm">Nenhum equipamento cadastrado.</td></tr>
                                    ` : maquinas.map(m => `
                                        <tr onclick="window.location.hash='#detalhe?eqp=${m.equipamento_id}'" class="hover:bg-gray-50 transition cursor-pointer">
                                            <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${m.equipamento_id}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${m.tipo || '---'} · ${m.modelo || ''}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${m.fazenda_nome || 'Não vinculada'}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span class="px-2.5 py-1 rounded-full text-[10px] font-bold border ${getBadge(m.classificacao)}">${m.classificacao || 'REGULAR'}</span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-xs font-mono font-bold">${m.score !== null && m.score !== undefined ? (m.score * 100).toFixed(1) + '%' : '---'}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right">
                                                <span class="text-xs font-bold text-[#DF082A] hover:underline">Ver Detalhes →</span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar detalhes do gestor.</p>`;
  }
}

function getBadge(cls) {
  if (cls === 'ALTO') return 'bg-red-50 text-red-700 border-red-200';
  if (cls === 'MEDIO') return 'bg-amber-50 text-amber-700 border-amber-200';
  return 'bg-emerald-50 text-emerald-700 border-emerald-200';
}