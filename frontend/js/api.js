/**
 * Centraliza as chamadas fetch e o gerenciamento de autenticação.
 */
import { getAuthHeaders, logout } from './auth.js';

const BASE_URL = window.location.origin;

function buildHeaders() {
  return {
    ...getAuthHeaders(),
    "Content-Type": "application/json"
  };
}

async function handleResponse(response) {
  if (response.status === 401) {
    logout();
    throw new Error("Sessao expirada.");
  }
  if (!response.ok) throw new Error(`Erro API: ${response.status}`);
  return response.json();
}

export async function fetchHistorico() {
  try {
    const response = await fetch(`${BASE_URL}/historico`, { headers: buildHeaders() });
    return await handleResponse(response);
  } catch (error) {
    console.error("Falha ao buscar histórico:", error);
    return [];
  }
}

export async function fetchPrevisao(equipamentoId) {
  try {
    const response = await fetch(`${BASE_URL}/previsao/${equipamentoId}`, {
      method: "POST",
      headers: buildHeaders()
    });
    return await handleResponse(response);
  } catch (error) {
    console.error(`Falha ao buscar previsão do equipamento ${equipamentoId}:`, error);
    return null;
  }
}