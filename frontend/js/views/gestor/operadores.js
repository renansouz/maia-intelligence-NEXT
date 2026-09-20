export async function renderGestorOperadores() {
  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div></div>`;

  try {
    const [resOps, resMaquinas] = await Promise.all([
      fetch('/usuarios/meus-operadores', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }),
      fetch('/maquinas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } })
    ]);

    const operadores = resOps.ok ? await resOps.json() : [];
    const maquinas = resMaquinas.ok ? await resMaquinas.json() : [];

    container.innerHTML = `
            <div class="space-y-8 animate-in fade-in duration-500">
                <div class="border-b border-gray-100 pb-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Operadores da Equipe</h3>
                        <p class="text-gray-500 text-sm">Lista de operadores de campo vinculados à sua gestão. Clique em um operador para inspecionar detalhes.</p>
                    </div>
                </div>

                <div class="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Nome</th>
                                    <th class="px-6 py-3 text-left text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Email</th>
                                    <th class="px-6 py-3 text-center text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Status</th>
                                    <th class="px-6 py-3 text-right text-[10px] font-bold text-gray-500 uppercase whitespace-nowrap">Ação</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-100">
                                ${operadores.length === 0 ? `
                                    <tr><td colspan="4" class="py-12 text-center text-gray-400 italic text-sm">Nenhum operador cadastrado na sua equipe.</td></tr>
                                ` : operadores.map(op => `
                                    <tr onclick='abrirDetalheOperador(${JSON.stringify(op).replace(/'/g, "&apos;")}, ${JSON.stringify(maquinas).replace(/'/g, "&apos;")})' class="hover:bg-gray-50 transition cursor-pointer">
                                        <td class="px-6 py-4 whitespace-nowrap text-xs font-bold text-gray-900">${op.nome}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-xs text-gray-600">${op.email}</td>
                                        <td class="px-6 py-4 whitespace-nowrap text-center">
                                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${op.ativo !== 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}">
                                                ${op.ativo !== 0 ? 'ATIVO' : 'INATIVO'}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right">
                                            <span class="text-xs font-bold text-blue-900 hover:underline">Ver Detalhes →</span>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Modal de Detalhe do Operador -->
            <div id="operador-modal" class="hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
                    <div class="flex justify-between items-center border-b pb-3">
                        <h4 class="font-extrabold text-gray-900 text-lg" id="modal-op-nome">Detalhes do Operador</h4>
                        <button onclick="document.getElementById('operador-modal').classList.add('hidden')" class="text-gray-400 hover:text-gray-700"><i data-lucide="x" class="w-5 h-5"></i></button>
                    </div>
                    <div id="modal-op-corpo" class="space-y-4 text-sm text-gray-700">
                        <!-- Conteúdo injetado via JS -->
                    </div>
                </div>
            </div>
        `;
    lucide.createIcons();
  } catch (e) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar operadores.</p>`;
  }
}

window.abrirDetalheOperador = async function (op, todasMaquinas) {
  const modal = document.getElementById('operador-modal');
  document.getElementById('modal-op-nome').textContent = op.nome;

  const corpo = document.getElementById('modal-op-corpo');
  corpo.innerHTML = `
        <div class="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-xl text-xs">
            <div><strong class="text-gray-400 block uppercase">Email</strong> ${op.email}</div>
            <div><strong class="text-gray-400 block uppercase">Status</strong> ${op.ativo !== 0 ? 'Ativo' : 'Inativo'}</div>
        </div>
        <div>
            <strong class="text-xs text-gray-400 block uppercase mb-2">Equipamentos Atribuídos</strong>
            <div id="modal-op-maquinas" class="space-y-2 max-h-48 overflow-y-auto">
                <div class="flex justify-center py-4"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-900"></div></div>
            </div>
        </div>
    `;
  modal.classList.remove('hidden');
  lucide.createIcons();

  try {
    // Consulta os detalhes de cada máquina em paralelo para filtrar apenas as vinculadas a este operador
    const promessas = todasMaquinas.map(m =>
      fetch(`/maquinas/${m.equipamento_id || m.EQUIPAMENTO_ID}/detalhe`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
      }).then(res => res.ok ? res.json() : null).catch(() => null)
    );

    const detalhesMaquinas = await Promise.all(promessas);

    // Filtra estritamente as máquinas onde o operador atual consta na lista de operadores vinculados
    const maquinasDoOperador = detalhesMaquinas.filter(m => {
      if (!m || !m.operadores) return false;
      return m.operadores.some(o => o.id_usuario === op.id_usuario);
    });

    const listaEl = document.getElementById('modal-op-maquinas');
    if (maquinasDoOperador.length === 0) {
      listaEl.innerHTML = `<p class="text-xs text-gray-400 italic">Nenhum equipamento vinculado a este operador no momento.</p>`;
    } else {
      listaEl.innerHTML = maquinasDoOperador.map(m => `
                <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-gray-200 text-xs">
                    <div>
                        <span class="font-bold text-gray-900">${m.equipamento_id}</span>
                        <span class="text-gray-500 text-[11px] block">${m.tipo || 'Ativo'} · ${m.modelo || ''}</span>
                    </div>
                    <a href="#detalhe?eqp=${m.equipamento_id}" onclick="document.getElementById('operador-modal').classList.add('hidden')" class="font-bold text-blue-950 hover:underline">Ver Máquina →</a>
                </div>
            `).join('');
    }
    lucide.createIcons();
  } catch (e) {
    document.getElementById('modal-op-maquinas').innerHTML = `<p class="text-xs text-red-500">Erro ao carregar máquinas do operador.</p>`;
  }
};