// src/store.js

import Vue from 'vue';
import Vuex from 'vuex';
import { api } from './services'; // Importa a API para interagir com o backend

Vue.use(Vuex);

export default new Vuex.Store({
  // --- STATE: Contém todos os dados reativos da aplicação ---
  state: {
    auth: {
      isLoggedIn: !!localStorage.getItem('authToken'), // Estado de login persistido
      username: localStorage.getItem('username') || '', // Nome do usuário
      token: localStorage.getItem('authToken') || '',   // Token de autenticação
      email: localStorage.getItem('email') || ''       // Email do usuário
    },
    showLabelModal: false, // Controla a visibilidade do modal de labels
  },

  // --- MUTATIONS: A única forma de alterar o estado de forma síncrona ---
  mutations: {
    // LOGIN: Atualiza o estado de autenticação e persiste dados no localStorage
    LOGIN(state, { username, email, token }) {
      state.auth.isLoggedIn = true;
      state.auth.username = username;
      state.auth.email = email;
      state.auth.token = token;
      localStorage.setItem('authToken', token);
      localStorage.setItem('username', username);
      localStorage.setItem('email', email);
    },
    // LOGOUT: Limpa o estado de autenticação e remove dados do localStorage
    LOGOUT(state) {
      state.auth.isLoggedIn = false;
      state.auth.username = '';
      state.auth.email = '';
      state.auth.token = '';
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      localStorage.removeItem('email');
    },
    SET_TOKEN(state, token) { state.auth.token = token; },
    // SET_USER_PROFILE_DATA: Atualiza o nome e email do usuário no estado (usado após GET de perfil)
    SET_USER_PROFILE_DATA(state, { name, email }) {
      state.auth.username = name;
      state.auth.email = email;
      localStorage.setItem('username', name);
      localStorage.setItem('email', email);
    },
    // SET_SHOW_LABEL_MODAL: Altera a visibilidade do modal de labels
    SET_SHOW_LABEL_MODAL(state, payload) { state.showLabelModal = payload; },
  },

  // --- ACTIONS: Disparam mutações e podem ter lógica assíncrona (chamadas de API) ---
  actions: {
    // login: Autentica o usuário via API e comita os dados no estado
    async login({ commit }, { email, senha }) {
      try {
        const responseData = await api.login(email, senha);
        const userDisplayName = responseData.name;
        const userEmailFromApi = responseData.email;
        const token = responseData.token;
        commit('LOGIN', { username: userDisplayName, email: userEmailFromApi, token });
        return responseData;
      } catch (error) {
        console.error('Erro ao fazer login:', error.response?.data || error.message);
        throw error;
      }
    },
    // logout: Desloga o usuário e limpa o estado
    async logout({ commit }) { await commit('LOGOUT'); },

    // fetchUserProfile: Busca dados do perfil do usuário logado via GET na API
    async fetchUserProfile({ commit, getters }) {
      if (getters.isUserLoggedIn && getters.getToken) {
        try {
          const userData = await api.getLoggedInUser(); // Chama a API para pegar o perfil
          if (userData && userData.name) {
            commit('SET_USER_PROFILE_DATA', { name: userData.name, email: userData.email });
          }
          return userData;
        } catch (error) {
          console.error('Erro ao buscar perfil do usuário logado:', error);
          if (error.message.includes('401') || error.message.includes('Token inválido') || error.message.includes('expirado')) {
            commit('LOGOUT'); // Desloga se o token for inválido
          }
          throw error;
        }
      }
    },
    // toggleLabelModal: Altera a visibilidade do modal de labels (usado pela NavBar)
    toggleLabelModal({ commit }, isVisible) { commit('SET_SHOW_LABEL_MODAL', isVisible); },
  },

  // --- GETTERS: Acessam e processam dados do estado de forma reativa ---
  getters: {
    isUserLoggedIn(state) { return state.auth.isLoggedIn; },
    getToken(state) { return state.auth.token; },
    getUserDisplayName(state) { return state.auth.username; }, // Retorna o nome de exibição do usuário
    getUserEmail(state) { return state.auth.email; },
    getShowLabelModal(state) { return state.showLabelModal; }, // Retorna a visibilidade do modal de labels
  }
});