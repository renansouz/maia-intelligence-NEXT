export function renderSompoCadastro() {
  const container = document.getElementById('view-content');
  container.innerHTML = `
        <div class="space-y-8 animate-in fade-in duration-500 max-w-2xl mx-auto">
            <div class="border-b border-gray-100 pb-4">
                <h3 class="text-2xl font-extrabold text-[#101828] tracking-tight">Cadastro de Máquinas na Apólice</h3>
                <p class="text-gray-500 text-sm">Adicione novos equipamentos corporativos à base global da Sompo.</p>
            </div>

            <div id="feedback-banner" class="hidden p-4 rounded-xl text-sm font-medium"></div>

            <form id="form-cad-maquina" class="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm space-y-5">
                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">ID do Equipamento (Ex: EQP-SP-01)</label>
                    <input type="text" id="eqp-id" required placeholder="EQP-SP-99"
                        class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#DF082A] transition">
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Tipo</label>
                        <input type="text" id="eqp-tipo" placeholder="Trator / Colheitadeira"
                            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#DF082A] transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Modelo</label>
                        <input type="text" id="eqp-modelo" placeholder="John Deere 8R"
                            class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#DF082A] transition">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Ano de Fabricação</label>
                    <input type="number" id="eqp-ano" placeholder="2023"
                        class="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#DF082A] transition">
                </div>

                <button type="submit" class="w-full bg-[#DF082A] text-white py-3.5 rounded-xl font-bold hover:bg-[#9E1E24] transition shadow-sm text-sm">
                    CADASTRAR MÁQUINA NA APÓLICE
                </button>
            </form>
        </div>
    `;
  lucide.createIcons();

  const form = document.getElementById('form-cad-maquina');
  const banner = document.getElementById('feedback-banner');

  form.onsubmit = async (e) => {
    e.preventDefault();
    banner.classList.add('hidden');

    const payload = {
      equipamento_id: document.getElementById('eqp-id').value.trim(),
      tipo: document.getElementById('eqp-tipo').value.trim() || null,
      modelo: document.getElementById('eqp-modelo').value.trim() || null,
      ano: document.getElementById('eqp-ano').value ? parseInt(document.getElementById('eqp-ano').value) : null
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

      banner.className = "p-4 rounded-xl text-sm font-medium bg-emerald-50 text-emerald-800 border border-emerald-200";
      banner.textContent = "Máquina cadastrada com sucesso na base da Sompo!";
      banner.classList.remove('hidden');
      form.reset();
    } catch (err) {
      banner.className = "p-4 rounded-xl text-sm font-medium bg-red-50 text-red-800 border border-red-200";
      banner.textContent = err.message;
      banner.classList.remove('hidden');
    }
  };
}