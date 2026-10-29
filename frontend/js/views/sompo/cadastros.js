export async function renderseguradoraCadastro() {
  const container = document.getElementById('view-content');
  container.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#DF082A]"></div></div>`;

  try {
    // Busca gestores e o catálogo de coberturas em paralelo
    const [resGestores, resCobertura] = await Promise.all([
      fetch('/gestores', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }),
      fetch('/cobertura/catalogo', { headers: { 'Authorization': `Bearer ${localStorage.getItem('maia_token')}` } }).catch(() => null)
    ]);

    const gestores = resGestores.ok ? await resGestores.json() : [];
    const catalogo = resCobertura && resCobertura.ok ? await resCobertura.json() : { "tipo": "BASICA" };

    container.innerHTML = `
            <div class="space-y-10 animate-in fade-in duration-500 max-w-5xl mx-auto">
                <div class="border-b border-gray-100 pb-4">
                    <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Cadastros e Gestão de Apólices</h3>
                    <p class="text-gray-500 text-sm">Gerencie a base global de equipamentos segurados e crie contas para os gestores de frota.</p>
                </div>

                <div id="feedback-banner" class="hidden p-4 rounded-xl text-sm font-medium"></div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    
                    <!-- 1. FORMULÁRIO: CADASTRAR MÁQUINA -->
                    <form id="form-cad-maquina" class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="tractor" class="w-5 h-5 text-[#DF082A]"></i> Cadastrar Nova Máquina
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">ID do Equipamento</label>
                            <input type="text" id="eqp-id" required placeholder="EQP-SP-99"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Gestor Responsável</label>
                            <select id="gestor-id" required
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                                <option value="">Selecione um gestor...</option>
                                ${gestores.map(g => `<option value="${g.id_usuario}">${g.nome} (${g.email})</option>`).join('')}
                            </select>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Tipo</label>
                                <input type="text" id="eqp-tipo" placeholder="Trator"
                                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Modelo</label>
                                <input type="text" id="eqp-modelo" placeholder="John Deere 8R"
                                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Ano</label>
                                <input type="number" id="eqp-ano" placeholder="2023"
                                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Valor Segurado (R$)</label>
                                <input type="number" step="any" id="eqp-valor" placeholder="350000.00"
                                    class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                            </div>
                        </div>
                        <button type="submit" class="w-full bg-[#DF082A] text-white py-3 rounded-xl font-bold hover:bg-[#9E1E24] transition text-sm">
                            CADASTRAR MÁQUINA
                        </button>
                    </form>

                    <!-- 2. FORMULÁRIO: CRIAR CONTA DE GESTOR -->
                    <form id="form-cad-gestor" class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-4">
                        <h4 class="font-extrabold text-gray-900 border-b pb-3 flex items-center gap-2">
                            <i data-lucide="user-plus" class="w-5 h-5 text-[#DF082A]"></i> Criar Conta de Gestor
                        </h4>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Nome Completo</label>
                            <input type="text" id="gestor-nome" required placeholder="Carlos Mendes"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Email Corporativo</label>
                            <input type="email" id="gestor-email" required placeholder="carlos@fazenda.com"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Senha Provisória</label>
                            <input type="password" id="gestor-senha" required minlength="6" placeholder="******"
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Tipo de Cobertura Contratada</label>
                            <select id="gestor-cobertura" required
                                class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[#DF082A]">
                                <option value="BASICA">Cobertura Básica (Incêndio, Colisão, Roubo)</option>
                                <option value="ADICIONAL">Cobertura Básica + Adicionais (Elétricos, etc.)</option>
                                <option value="PARTICULAR">Cobertura Completa Particular</option>
                            </select>
                        </div>
                        <button type="submit" class="w-full bg-gray-900 text-white py-3 rounded-xl font-bold hover:bg-black transition text-sm">
                            CRIAR CONTA DE GESTOR
                        </button>
                    </form>

                </div>
            </div>
        `;
    lucide.createIcons();

    const banner = document.getElementById('feedback-banner');

    // Submissão de Máquina
    document.getElementById('form-cad-maquina').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const payload = {
        equipamento_id: document.getElementById('eqp-id').value.trim(),
        gestor_id: parseInt(document.getElementById('gestor-id').value),
        tipo: document.getElementById('eqp-tipo').value.trim() || null,
        modelo: document.getElementById('eqp-modelo').value.trim() || null,
        ano: document.getElementById('eqp-ano').value ? parseInt(document.getElementById('eqp-ano').value) : null,
        valor_segurado: document.getElementById('eqp-valor').value ? parseFloat(document.getElementById('eqp-valor').value) : null
      };

      try {
        const res = await fetch('/maquinas', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('maia_token')}`
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "Erro ao cadastrar máquina.");
        }

        mostrarFeedback("Máquina cadastrada com sucesso na apólice!", "success");
        e.target.reset();
      } catch (err) {
        mostrarFeedback(err.message, "error");
      }
    };

    // Submissão de Gestor
    document.getElementById('form-cad-gestor').onsubmit = async (e) => {
      e.preventDefault();
      banner.classList.add('hidden');

      const payload = {
        nome: document.getElementById('gestor-nome').value.trim(),
        email: document.getElementById('gestor-email').value.trim(),
        senha: document.getElementById('gestor-senha').value,
        papel: "GESTOR",
        tipo_cobertura: document.getElementById('gestor-cobertura').value
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
          throw new Error(err.detail || "Erro ao criar conta de gestor.");
        }

        mostrarFeedback("Conta de gestor criada com sucesso!", "success");
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

  } catch (error) {
    container.innerHTML = `<p class="text-center py-10 text-red-500">Erro ao carregar módulo de cadastros.</p>`;
  }
}