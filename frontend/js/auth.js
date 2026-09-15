/**
 * Guarda token/papel/nome no localStorage e protege as telas da SPA.
 */
const TOKEN_KEY = 'maia_token';
const PAPEL_KEY = 'maia_papel';
const NOME_KEY = 'maia_nome';

export function salvarSessao(token, papel, nome) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(PAPEL_KEY, papel);
  localStorage.setItem(NOME_KEY, nome);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getPapel() {
  return localStorage.getItem(PAPEL_KEY);
}

export function getNome() {
  return localStorage.getItem(NOME_KEY);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(PAPEL_KEY);
  localStorage.removeItem(NOME_KEY);
  window.location.href = 'login.html';
}

export function exigirAutenticacao() {
  if (!getToken()) {
    window.location.href = 'login.html';
  }
}

export function getAuthHeaders() {
  return { "Authorization": `Bearer ${getToken()}` };
}