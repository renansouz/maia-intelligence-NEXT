export async function renderGestorCadastro() {
  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-900"></div></div>`;

  try {
    // Carrega dados necessários para os selects de vínculos em paralelo
    const [resFazendas, resMaquinasSemFazenda, resMinhasMaquinas] = await Promise.all([
      fetch('/fazendas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }),
      fetch('/maquinas/sem-fazenda', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }),
      fetch('/maquinas', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } })
    ]);

    const fazendas = resFazendas.ok ? await resFazendas.json() : [];
    const maquinasSemFazenda = resMaquinasSemFazenda.ok ? await resMaquinasSemFazenda.json() : [];
    const minhasMaquinas = resMinhasMaquinas.ok ? await resMinhasMaquinas.json() : [];

    container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-500 max-w-5xl mx-auto">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Cadastros e Vínculos Operacionais</h3>
                    <p class="text-gray-500 text-sm">Gerencie propriedades, cadastre operadores e vincule ativos da frota.</p>
                </div>

                <div id="feedback-banner" class="hidden p-4 rounded-xl text-sm font-medium"></div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    
                    <!-- 1. CADASTRAR FAZENDA -->
                    <form id="form-fazenda" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="home" class="w-5 h-5 text-blue-900"></i> Nova Propriedade (Fazenda)
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nome da Propriedade</label>
                            <input type="text" id="fazenda-nome" required placeholder="Fazenda Boa Vista"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Cidade</label>
                            <input type="text" id="fazenda-cidade" required placeholder="Campinas"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Endereço / Referência (Opcional)</label>
                            <input type="text" id="fazenda-end" placeholder="Rodovia SP-330, Km 280"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <button type="submit" class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                            CADASTRAR PROPRIEDADE
                        </button>
                    </form>

                    <!-- 2. CADASTRAR OPERADOR -->
                    <form id="form-operador" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="user-plus" class="w-5 h-5 text-blue-900"></i> Novo Operador de Campo
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nome Completo</label>
                            <input type="text" id="op-nome" required placeholder="João da Silva"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Email de Acesso</label>
                            <input type="email" id="op-email" required placeholder="joao@operador.com"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Senha Provisória</label>
                            <input type="password" id="op-senha" required minlength="6" placeholder="******"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <button type="submit" class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                            CADASTRAR OPERADOR
                        </button>
                    </form>

                    <!-- 3. VINCULAR MÁQUINA À FAZENDA -->
                    <form id="form-vincular-fazenda" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="link" class="w-5 h-5 text-blue-900"></i> Vincular Máquina à Propriedade
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Equipamento sem Propriedade</label>
                            <select id="vinc-eqp-id" required
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                                <option value="">Selecione a máquina...</option>
                                ${maquinasSemFazenda.map(m => `<option value="${m.equipamento_id}">${m.equipamento_id} (${m.modelo || m.tipo || 'N/D'})</option>`).join('')}
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Propriedade (Fazenda)</label>
                            <select id="vinc-fazenda-id" required
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                                <option value="">Selecione a fazenda...</option>
                                ${fazendas.map(f => `<option value="${f.id_fazenda}">${f.nome}</option>`).join('')}
                            </select>
                        </div>
                        <button type="submit" class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                            VINCULAR MÁQUINA À FAZENDA
                        </button>
                    </form>

                    <!-- 4. VINCULAR OPERADOR À MÁQUINA -->
                    <form id="form-vincular-operador" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="user-check" class="w-5 h-5 text-blue-900"></i> Atribuir Operador à Máquina
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Equipamento da Frota</label>
                            <select id="op-vinc-eqp" required
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                                <option value="">Selecione a máquina...</option>
                                ${minhasMaquinas.map(m => `<option value="${m.equipamento_id}">${m.equipamento_id} (${m.modelo || m.tipo || 'N/D'})</option>`).join('')}
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Operador Disponível</label>
                            <select id="op-vinc-id" required disabled
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900 disabled:bg-gray-100">
                                <option value="">Primeiro selecione a máquina...</option>
                            </select>
                        </div>
                        <button type="submit" id="btn-vinc-op" disabled class="w-full bg-blue-900 text-white py-3 rounded-xl font-bold hover:bg-blue-950 transition text-sm disabled:opacity-50">
                            ATRIBUIR OPERADOR AO ATIVO
                        </button>
                    </form>

                </div>
            </div>
        `;
    lucide.createIcons();

    const banner = document.getElementById('feedback-banner');

    // Handler: Cadastrar Fazenda
    document.getElementById('form-fazenda').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const payload = {
        nome: document.getElementById('fazenda-nome').value.trim(),
        cidade: document.getElementById('fazenda-cidade').value.trim(),
        endereco: document.getElementById('fazenda-end').value.trim() || null
      };

      try {
        const res = await fetch('/fazendas', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` },
          body: JSON.stringify(payload)
        });
        if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || "Erro ao cadastrar fazenda."); }
        mostrarFeedback("Propriedade cadastrada com sucesso!", "success");
        setTimeout(() => renderGestorCadastro(), 1000);
      } catch (err) { mostrarFeedback(err.message, "error"); }
    };

    // Handler: Cadastrar Operador
    document.getElementById('form-operador').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const payload = {
        nome: document.getElementById('op-nome').value.trim(),
        email: document.getElementById('op-email').value.trim(),
        senha: document.getElementById('op-senha').value,
        papel: "OPERADOR"
      };

      try {
        const res = await fetch('/usuarios', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` },
          body: JSON.stringify(payload)
        });
        if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || "Erro ao cadastrar operador."); }
        mostrarFeedback("Operador cadastrado com sucesso!", "success");
        setTimeout(() => renderGestorCadastro(), 1000);
      } catch (err) { mostrarFeedback(err.message, "error"); }
    };

    // Handler: Vincular Máquina à Fazenda
    document.getElementById('form-vincular-fazenda').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const eqpId = document.getElementById('vinc-eqp-id').value;
      const fazendaId = parseInt(document.getElementById('vinc-fazenda-id').value);

      try {
        const res = await fetch(`/maquinas/${eqpId}/vincular-fazenda`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` },
          body: JSON.stringify({ fazenda_id: fazendaId })
        });
        if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || "Erro ao vincular máquina."); }
        mostrarFeedback("Máquina vinculada à propriedade com sucesso!", "success");
        setTimeout(() => renderGestorCadastro(), 1000);
      } catch (err) { mostrarFeedback(err.message, "error"); }
    };

    // Handler Dinâmico: Quando seleciona a máquina, busca os operadores disponíveis para ela
    const selectEqpOp = document.getElementById('op-vinc-eqp');
    const selectOpId = document.getElementById('op-vinc-id');
    const btnVincOp = document.getElementById('btn-vinc-op');

    selectEqpOp.onchange = async () => {
      const eqpId = selectEqpOp.value;
      if (!eqpId) {
        selectOpId.innerHTML = `<option value="">Primeiro selecione a máquina...</option>`;
        selectOpId.disabled = true;
        btnVincOp.disabled = true;
        return;
      }

      selectOpId.innerHTML = `<option value="">Carregando operadores...</option>`;
      selectOpId.disabled = true;

      try {
        const res = await fetch(`/maquinas/${eqpId}/operadores-disponiveis`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` }
        });
        const ops = res.ok ? await res.json() : [];

        if (ops.length === 0) {
          selectOpId.innerHTML = `<option value="">Nenhum operador disponível para vínculo</option>`;
          selectOpId.disabled = true;
          btnVincOp.disabled = true;
        } else {
          selectOpId.innerHTML = `<option value="">Selecione o operador...</option>` + ops.map(o => `<option value="${o.id_usuario}">${o.nome} (${o.email})</option>`).join('');
          selectOpId.disabled = false;
          btnVincOp.disabled = false;
        }
      } catch (e) {
        selectOpId.innerHTML = `<option value="">Erro ao carregar operadores</option>`;
      }
    };

    // Handler: Vincular Operador à Máquina
    document.getElementById('form-vincular-operador').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const eqpId = selectEqpOp.value;
      const operadorId = parseInt(selectOpId.value);

      try {
        const res = await fetch(`/maquinas/${eqpId}/vincular-operador`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` },
          body: JSON.stringify({ operador_id: operadorId })
        });
        if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || "Erro ao atribuir operador."); }
        mostrarFeedback("Operador atribuído à máquina com sucesso!", "success");
        setTimeout(() => renderGestorCadastro(), 1000);
      } catch (err) { mostrarFeedback(err.message, "error"); }
    };

    function mostrarFeedback(msg, tipo) {
      banner.className = `p-4 rounded-xl text-sm font-medium ${tipo === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'}`;
      banner.textContent = msg;
      banner.classList.remove('hidden');
    }

  } catch (error) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar módulo de cadastros.</p>`;
  }
}