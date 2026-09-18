const BASE_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();

  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');

  if (!token) {
    showError("Link de acesso inválido. Nenhum token encontrado na URL.");
    return;
  }

  // Preenche data e hora atuais por padrão
  const agora = new Date();
  const dataInput = document.getElementById('data');
  const horaInput = document.getElementById('hora');

  if (dataInput) dataInput.value = agora.toISOString().split('T')[0];
  if (horaInput) horaInput.value = agora.toTimeString().split(' ')[0].substring(0, 5);

  await carregarDadosManutencao(token);
});

async function carregarDadosManutencao(token) {
  try {
    const response = await fetch(`${BASE_URL}/manutencao/externo/${token}`);

    if (!response.ok) {
      throw new Error("Este link já foi utilizado ou expirou. Entre em contato com quem solicitou a manutenção para gerar um novo link.");
    }

    const data = await response.json();

    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('form-state').classList.remove('hidden');

    // Exibe dados da máquina e o motivo solicitado pelo gestor
    document.getElementById('eqp-id').textContent = data.equipamento_id || 'Ativo Rural';
    const descSolicitada = document.getElementById('motivo-solicitado');
    if (descSolicitada) {
      descSolicitada.textContent = data.descricao || data.motivo || 'Manutenção preventiva solicitada pelo gestor da frota.';
    }

    const form = document.getElementById('form-manutencao');
    if (form) {
      form.onsubmit = (e) => concluirManutencao(e, token);
    }

  } catch (error) {
    showError(error.message);
  }
}

async function concluirManutencao(e, token) {
  e.preventDefault();
  const btn = document.getElementById('btn-submit');
  const errorBanner = document.getElementById('form-error');

  if (errorBanner) errorBanner.classList.add('hidden');
  btn.disabled = true;
  btn.textContent = "Registrando manutenção...";

  const payload = {
    data_realizada: document.getElementById('data').value,
    hora_realizada: document.getElementById('hora').value,
    descricao: document.getElementById('descricao').value.trim()
  };

  try {
    const response = await fetch(`${BASE_URL}/manutencao/externo/${token}/concluir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({}));
      throw new Error(errJson.detail || "Não foi possível registrar a manutenção. O link pode ter expirado.");
    }

    // Transição limpa para a tela de sucesso definitiva
    document.getElementById('form-state').classList.add('hidden');
    document.getElementById('success-state').classList.remove('hidden');
    lucide.createIcons();

  } catch (error) {
    if (errorBanner) {
      errorBanner.textContent = error.message;
      errorBanner.classList.remove('hidden');
    }
    btn.disabled = false;
    btn.textContent = "REGISTRAR MANUTENÇÃO";
  }
}

function showError(msg) {
  document.getElementById('loading-state').classList.add('hidden');
  const errEl = document.getElementById('error-state');
  if (errEl) {
    errEl.classList.remove('hidden');
    document.getElementById('error-message').textContent = msg;
  }
}