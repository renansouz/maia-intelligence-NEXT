const BASE_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();

  // Pega o token da URL (ex: manutencao.html?token=abc123xyz)
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');

  if (!token) {
    showError("Nenhum código de acesso foi fornecido na URL.");
    return;
  }

  // Preenche data e hora com o momento atual para facilitar pro técnico
  const agora = new Date();
  document.getElementById('data').value = agora.toISOString().split('T')[0];
  document.getElementById('hora').value = agora.toTimeString().split(' ')[0].substring(0, 5);

  await carregarDadosMaquina(token);
});

async function carregarDadosMaquina(token) {
  try {
    const response = await fetch(`${BASE_URL}/manutencao/externo/${token}`);

    if (!response.ok) {
      throw new Error("Este link expirou, é inválido, ou a manutenção já foi registrada.");
    }

    const data = await response.json();

    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('form-state').classList.remove('hidden');
    document.getElementById('eqp-id').textContent = data.equipamento_id;

    document.getElementById('form-manutencao').addEventListener('submit', (e) => concluirManutencao(e, token));

  } catch (error) {
    showError(error.message);
  }
}

async function concluirManutencao(e, token) {
  e.preventDefault();
  const btn = document.getElementById('btn-submit');

  // Evita duplo clique
  btn.disabled = true;
  btn.innerHTML = `<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div> Registrando...`;

  const payload = {
    data_realizada: document.getElementById('data').value,
    hora_realizada: document.getElementById('hora').value,
    descricao: document.getElementById('descricao').value
  };

  try {
    const response = await fetch(`${BASE_URL}/manutencao/externo/${token}/concluir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error("Ocorreu um erro ao tentar salvar. Tente novamente.");
    }

    // Sucesso
    document.getElementById('form-state').classList.add('hidden');
    document.getElementById('success-state').classList.remove('hidden');

  } catch (error) {
    alert(error.message);
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="check-circle" class="w-5 h-5"></i> REGISTRAR MANUTENÇÃO`;
    lucide.createIcons();
  }
}

function showError(msg) {
  document.getElementById('loading-state').classList.add('hidden');
  const errEl = document.getElementById('error-state');
  errEl.classList.remove('hidden');
  document.getElementById('error-message').textContent = msg;
}