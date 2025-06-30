// src/router.js

import Vue from 'vue';
import VueRouter from 'vue-router';
import store from './store'; // Importa o store Vuex para gerenciar o estado global

Vue.use(VueRouter); // Habilita o Vue Router na aplicação

// Importa os componentes principais para cada rota
import HomePage from "./views/Home.vue";
import LoginPage from "./views/Login.vue";
import CadastroPage from "./views/Cadastro.vue";
import UserPage from "./views/User/Main.vue";
// O ModalLabels não é importado aqui; ele é um componente filho em UserPage, controlado por v-if.

// Define as rotas da sua aplicação
const routes = [
  { path: "/", name: "Home", component: HomePage },
  { path: "/login", name: "Login", component: LoginPage },
  { path: "/cadastro", name: "Cadastro", component: CadastroPage },
  {
    path: "/user",
    name: "User",
    component: UserPage,
    meta: { requiresAuth: true }, // **Meta-dado:** Esta rota exige que o usuário esteja autenticado.
    // O modal de labels não é uma rota filha aqui; ele é um componente interno de UserPage.
  },
];

// Cria a instância do Vue Router
const router = new VueRouter({
  mode: 'history', // URLs limpas (ex: /user em vez de /#/user)
  routes,          // Usa as rotas definidas
});

// --- Navigation Guard Global: Lógica de Autenticação ---
// Executado antes de cada navegação para controlar o acesso às rotas.
router.beforeEach((to, from, next) => {
    const isLoggedIn = store.getters.isUserLoggedIn; // Status de login do usuário
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth); // A rota de destino exige autenticação?
    const isPublicAuthPath = ['/login', '/cadastro'].includes(to.path); // A rota de destino é login/cadastro?

    // 1. Proteger rotas autenticadas: Se a rota exige login e o usuário não está logado, redireciona.
    if (requiresAuth && !isLoggedIn) {
        console.log(`Guard: Rota ${to.path} requer autenticação. Redirecionando para /login.`);
        next('/login');
    }
    // 2. Bloquear login/cadastro para logados: Se já está logado e tenta ir para login/cadastro, redireciona para /user.
    else if (isLoggedIn && isPublicAuthPath) {
        console.log(`Guard: Já logado. Redirecionando de ${to.path} para /user.`);
        next('/user');
    }
    // 3. Gerenciar rota raiz ('/'): Se está na home, redireciona logados para /user, deslogados ficam na home.
    else if (to.path === '/') {
        if (isLoggedIn) {
            console.log('Guard: Logado na Home. Redirecionando para /user.');
            next('/user');
        } else {
            console.log('Guard: Deslogado na Home. Permitindo acesso.');
            next();
        }
    }
    // 4. Permitir outras navegações: Se nenhuma das regras acima se aplica, a navegação é permitida.
    else {
        console.log(`Guard: Permitindo navegação para ${to.path}.`);
        next();
    }
});

export default router; // Exporta o router para ser usado em `main.js`