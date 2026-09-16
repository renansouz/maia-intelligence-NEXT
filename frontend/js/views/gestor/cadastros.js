export function renderGestorCadastro() {
  const container = document.getElementById('view-content');
  container.innerHTML = `
        <div class="space-y-10 animate-in fade-in duration-500 max-w-3xl mx-auto">
            <div class="border-b border-gray-100 pb-4">
                <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Cadastros e Gestão de Equipe</h3>
                <p class="text-gray-500 text-sm">Registre propriedades rurais e cadastre operadores vinculados à sua gestão.</p>
            </div>

            <div id="feedback-banner" class="hidden p-4 rounded-xl text-sm font-medium"></div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                
                <!-- Formulário de Fazenda -->
                <form id="form-fazenda" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                    <h4 class="font-bold text-gray-900 border-b pb-2 flex items-center gap-2">
                        <i data-lucide="home" class="w-4 h-4 text-blue-900"></i> Nova Fazenda
                    </h4>
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nome da Propriedade</label>
                        <input type="text" id="fazenda-nome" required placeholder="Fazenda Boa Vista"
                            class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Latitude</label>
                            <input type="number" step="any" id="fazenda-lat" required placeholder="-21.17"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Longitude</label>
                            <input type="number" step="any" id="fazenda-lon" required placeholder="-47.81"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Endereço / Localidade</label>
                        <input type="text" id="fazenda-end" placeholder="Rodovia SP-330, Km 280"
                            class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900">
                    </div>
                    <button type="submit" class="w-full bg-blue-900 text-white py-2.5 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                        CADASTRAR FAZENDA
                    </button>
                </form>

                <!-- Formulário de Operador -->
                <form id="form-operador" class="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
                    <h4 class="font-bold text-gray-900 border-b pb-2 flex items-center gap-2">
                        <i data-lucide="user-plus" class="w-4 h-4 text-blue-900"></i> Novo Operador
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
                    <button type="submit" class="w-full bg-blue-900 text-white py-2.5 rounded-xl font-bold hover:bg-blue-950 transition text-sm">
                        CADASTRAR OPERADOR
                    </button>
                </form>

            </div>
        </div>
    `;
  lucide.createIcons();

  const banner = document.getElementById('feedback-banner');

  document.getElementById('form-fazenda').onsubmit = async (e) => {
    e.preventDefault();
    banner.classList.add('hidden');

    const payload = {
      nome: document.getElementById('fazenda-nome').value.trim(),
      latitude: parseFloat(document.getElementById('fazenda-lat').value),
      longitude: parseFloat(document.getElementById('fazenda-lon').value),
      endereco: document.getElementById('fazenda-end').value.trim() || null
    };

    try {
      const res = await fetch('/fazendas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Erro ao cadastrar fazenda.");
      }

      mostrarFeedback("Fazenda cadastrada com sucesso!", "success");
      e.target.reset();
    } catch (err) {
      mostrarFeedback(err.message, "error");
    }
  };

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
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Erro ao cadastrar operador.");
      }

      mostrarFeedback("Operador cadastrado com sucesso!", "success");
      e.target.reset();
    } catch (err) {
      mostrarFeedback(err.message, "error");
    }
  };

  function mostrarFeedback(msg, tipo) {
    banner.className = `p-4 rounded-xl text-sm font-medium ${tipo === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'}`;
    banner.textContent = msg;
    banner.classList.remove('hidden');
  }
}