// src/components/NavBar.vue

<template lang="pug">
  nav.navbar
    ul.left
      li.logo
        router-link(to="/")
    ul.right
      template(v-if="isLoggedIn")
        li.manage-labels(@click="openLabelModal") Gerenciar Labels
        li.logout(@click="logoutAndRedirect") Logout
      template(v-else)
        li.login
          router-link(to="/login") Sign in
        li.cadastro
          router-link(to="/cadastro") Sign up
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex';

export default {
  name: "NavBar",
  async created() {
    console.log('NavBar Created. isLoggedIn:', this.isLoggedIn, 'Current Display Name:', this.getUserDisplayName); // Debug 1

    if (this.isLoggedIn && !this.getUserDisplayName) { // <--- Condição importante
      console.log('NavBar: Logged in but display name is missing. Attempting to fetch user profile...'); // Debug 2
      try {
        await this.fetchUserProfile();
        console.log('NavBar: User profile fetched successfully. New Display Name:', this.getUserDisplayName); // Debug 3
      } catch (error) {
        console.error("NavBar: Error fetching user profile:", error); // Debug 4
      }
    } else if (this.isLoggedIn) {
        console.log('NavBar: Already logged in with display name:', this.getUserDisplayName); // Debug 5
    }
  },
  computed: {
    ...mapState({
      isLoggedIn: state => state.auth.isLoggedIn,
    }),
    ...mapGetters([
      'getUserDisplayName',
    ])
  },
  methods: {
    // REINTRODUZIDO: toggleLabelModal aqui
    ...mapActions(['logout', 'toggleLabelModal', 'fetchUserProfile']),

    async logoutAndRedirect() {
      try {
        await this.logout();
        this.$router.push('/');
      } catch (error) {
        console.error("Erro durante o processo de logout e redirecionamento:", error);
      }
    },

    // VOLTAR A USAR AÇÃO VUEX para mostrar o modal
    openLabelModal() {
      this.toggleLabelModal(true); // <-- CHAMA A AÇÃO VUEX PARA ABRIR O MODAL
    },
  }
}
</script>

<style lang="scss" scoped>
// Seus estilos SCSS aqui (não foram alterados)
$primary-blue: #30ABD3;
$text-light: #fff;
$text-dark-blue: #30ABD3;
$hover-light-blue: #e0f2f7;

.navbar {
  display: flex;
  justify-content: space-between;
  background-color: $text-light;
  padding: 10px;
}

.left, .right {
  list-style-type: none;
  padding: 0 20px;
  margin: 0;

  li {
    display: inline;
    margin-right: 20px;

    &:last-child {
      margin-right: 0;
    }
  }
}

.left {
  background-color: $primary-blue;
  border-radius: 30px;
  padding: 20px;

  .logo {
    width: 50px;
    height: 50px;
    a {
      display: block;
      width: 100%;
      height: 100%;
    }
  }
}

.right {
  display: flex;
  align-items: center;

  .login, .logout, .manage-labels, .cadastro {
    padding: 10px;
    border-radius: 50px;
    border: 1px solid $primary-blue;
    cursor: pointer;
    transition: all 0.3s ease;

    a {
      text-decoration: none;
    }
  }

  .login, .logout, .manage-labels, .user {
    color: $text-dark-blue;
  }

  .cadastro {
    background-color: $primary-blue;
    a {
      color: $text-light;
    }
  }

  .login:hover,
  .logout:hover,
  .manage-labels:hover {
    background-color: $hover-light-blue;
  }

  a {
    color: inherit;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.user {
  padding: 10px;
}
</style>