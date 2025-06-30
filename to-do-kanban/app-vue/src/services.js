// src/services/api.js

import store from './store'; // Importa o Vuex store para acessar o token de autenticação

const API_URL = "http://127.0.0.1:5000"; // URL base do seu backend

// Função utilitária para fazer requisições HTTP autenticadas
async function customFetch(endpoint, options = {}) {
  const token = store.getters.getToken || localStorage.getItem('authToken'); // Pega o token do store ou localStorage

  const headers = {
    'Content-Type': 'application/json', // Define o tipo de conteúdo padrão como JSON
    ...options.headers, // Permite sobrescrever ou adicionar outros cabeçalhos
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`; // Adiciona o token de autenticação (Bearer Token)
  }

  const config = {
    ...options, // Mescla opções adicionais (method, body, etc.)
    headers,    // Aplica os cabeçalhos configurados
  };

  const response = await fetch(`${API_URL}${endpoint}`, config); // Executa a requisição

  // Trata respostas de erro da API
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido do servidor.' }));
    console.error(`Erro na requisição ${endpoint}:`, errorData);
    throw new Error(errorData.erro || errorData.message || 'Erro desconhecido'); // Lança um erro com a mensagem da API
  }

  // Retorna null para respostas sem conteúdo (ex: 204 No Content)
  if (response.status === 204) {
    return null;
  }

  return response.json(); // Retorna os dados JSON da resposta
}

// Objeto 'api' com métodos para interagir com diferentes endpoints
export const api = {
  // Login de usuário
  async login(email, password) {
    const response = await customFetch('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response; // Retorna a resposta completa da API (inclui token e dados do usuário)
  },
  // Criação de novo usuário
  async createUser(userData) {
    return customFetch('/usuarios', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Busca dados de usuários (pode ser todos ou específico, dependendo do backend)
  async getUserData() {
    return customFetch('/usuarios');
  },

  // Busca dados do usuário logado (requer token)
  async getLoggedInUser() {
    return customFetch('/usuarios/meu-perfil'); // Endpoint para o perfil do usuário logado
  },

  // Atualização parcial de recursos (PATCH)
  async patch(url, data) {
    return customFetch(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  // Criação de nova tarefa
  async createTask(newTask) {
    return customFetch('/tasks', {
      method: 'POST',
      body: JSON.stringify(newTask),
    });
  },

  // Exclusão de tarefa por ID
  async deleteTask(taskId) {
    return customFetch(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },

  // Criação de nova label
  async createLabel(newLabel) {
    return customFetch('/labels', {
      method: 'POST',
      body: JSON.stringify({ name: newLabel.name, hex_color: newLabel.hex_color }),
    });
  },

  // Busca todas as labels
  async getLabels() {
    return customFetch('/labels');
  },

  // Atualização de label por ID
  async updateLabel(labelId, updatedLabel) {
    return customFetch(`/labels/${labelId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name: updatedLabel.name, hex_color: updatedLabel.hex_color }),
    });
  },

  // Exclusão de label por ID
  async deleteLabel(labelId) {
    return customFetch(`/labels/${labelId}`, {
      method: 'DELETE',
    });
  },

  // Vincula uma label a uma tarefa
  async linkLabelToTask(taskId, labelId) {
    return customFetch(`/tasks/${taskId}/labels`, {
      method: 'POST',
      body: JSON.stringify({ label_id: labelId }),
    });
  },

  // Desvincula uma label de uma tarefa
  async unlinkLabelFromTask(taskId, labelId) {
    return customFetch(`/tasks/${taskId}/labels/${labelId}`, {
      method: 'DELETE',
    });
  },
};