/**
 * Módulo de integração com a API MAIA.
 * Centraliza as chamadas fetch e o gerenciamento de headers de segurança.
 */
import { API_KEY } from './config.js';
const BASE_URL = window.location.origin;

const headers = {
  "X-API-KEY": API_KEY,
  "Content-Type": "application/json"
};

export async function fetchHistorico() {
  try {
    const response = await fetch(`${BASE_URL}/historico`, { headers });
    if (!response.ok) throw new Error(`Erro API: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Falha ao buscar histórico:", error);
    return [];
  }
}

export async function fetchPrevisao(equipamentoId) {
  try {
    const response = await fetch(`${BASE_URL}/previsao/${equipamentoId}`, { headers });
    if (!response.ok) throw new Error(`Erro API: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Falha ao buscar previsão do equipamento ${equipamentoId}:`, error);
    return null;
  }
}