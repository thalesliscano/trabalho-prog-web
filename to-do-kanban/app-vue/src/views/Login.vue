<template lang="pug">
section.login-page
  h1 Login 
  form(@submit.prevent="logar")
    div.form-group
      label(for="email") Email
      input(type="email" name="email" id="email" v-model="loginForm.email" required)
    div.form-group
      label(for="senha") Password 
      input(type="password" name="senha" id="senha" v-model="loginForm.senha" required) 
    router-link(to="/cadastro") Register here! 
    button.btn Logar 
</template>

<script>
import { mapActions } from 'vuex'; // Importa 'mapActions' para mapear ações do Vuex

export default {
  name: 'LoginPage', // Nome do componente Vue
  data() {
    return {
      loginForm: { // Objeto para armazenar os dados do formulário
        email: '',
        senha: ''
      }
    };
  },
  methods: {
    ...mapActions(['login']), // Mapeia a ação 'login' do Vuex store (assíncrona)

    async logar() { // Método assíncrono para lidar com o envio do formulário de login
      try {
        const { email, senha } = this.loginForm; // Desestrutura email e senha do formulário
        console.log("Tentando login com:", email, senha); // Log de depuração

        await this.login({ email, senha }); // Chama a ação 'login' do Vuex. Espera a conclusão.

        this.$router.push('/user'); // Redireciona o usuário para a página '/user' após login bem-sucedido
      } catch (error) {
        // Captura e exibe erros de login (ex: credenciais inválidas)
        console.error('Erro ao fazer login:', error.response?.data || error.message);
        alert('Erro ao fazer login: ' + (error.response?.data?.message || 'Verifique suas credenciais.')); // Alerta o usuário
      }
    }
  }
};
</script>

<style lang="scss" scoped> // Estilos SCSS com escopo para este componente
// Variáveis SCSS para padronização de cores e dimensões
$primary-blue: #30ABD3;
$text-light: #fff;
$text-dark: #000;
$border-light: #fff;
$border-dark: #000;
$input-focus-bg: rgba($text-dark, 0.02);
$button-bg: #fff;
$button-color: $primary-blue;
$button-hover-bg: lighten($primary-blue, 40%);
$link-color: #fff;
$link-hover-color: darken($link-color, 20%);
$shadow-color: rgba(0, 0, 0, 0.2);

.login-page { // Estilos para o contêiner principal do login
  display: flex;
  flex-direction: column;
  width: 300px;
  height: auto;
  margin: 100px auto 0;
  padding: 20px;
  border-radius: 10px;
  background-color: $primary-blue; // Cor de fundo do card de login
  box-shadow: 0 5px 15px $shadow-color;
  border: none;

  h1 { // Estilos para o título
    text-align: center;
    margin-bottom: 20px;
    color: $text-light;
    font-weight: bold;
    font-size: 35px;
  }

  form { // Estilos para o formulário
    display: flex;
    flex-direction: column;
    margin: 0 auto;

    .form-group { // Estilos para o agrupamento de campos do formulário
      display: flex;
      flex-direction: column;
      margin-bottom: 15px;
    }

    input { // Estilos para os campos de input
      width: 250px;
      height: 35px;
      border-radius: 50px;
      border: 2px solid $border-light;
      color: $text-dark;
      font-weight: bold;
      text-align: center;
      margin-top: 5px;
      font-size: 1em;
      background-color: transparent;

      &:focus { // Estilos para o input em foco
        border: 2px solid $border-dark;
        background: $input-focus-bg;
        outline: none;
      }
    }

    label { // Estilos para os rótulos dos campos
      text-transform: capitalize;
      font-weight: 600;
      color: $text-light;
      margin-bottom: 5px;
    }

    .btn { // Estilos para o botão de login
      align-self: flex-end;
      padding: 8px 15px;
      width: auto;
      margin-top: 20px;
      background: $button-bg;
      border: none;
      border-radius: 50px;
      color: $button-color;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.3s ease, color 0.3s ease;

      &:hover { // Estilos para o botão ao passar o mouse
        background: $button-hover-bg;
        color: $primary-blue;
      }
    }

    a { // Estilos para o link de cadastro
      color: $link-color;
      text-decoration: none;
      font-size: 0.9em;
      margin-top: 10px;
      text-align: center;

      &:hover { // Estilos para o link ao passar o mouse
        text-decoration: underline;
        color: $link-hover-color;
      }
    }
  }
}
</style>