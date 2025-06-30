<template lang="pug">
section.cadastro-page
  h1 Cadastro de Usuário
  form(@submit.prevent="cadastrar")
    div.form-group 
      label(for="name") Nome
      input(type="text" name="name" id="name" v-model="cadastroForm.name" required)
    div.form-group 
      label(for="email") Email
      input(type="email" name="email" id="email" v-model="cadastroForm.email" required)
    div.form-group 
      label(for="password") Senha
      input(type="password" name="password" id="password" v-model="cadastroForm.password" required)
    button(type="submit" class="btn") Cadastrar
  p Já tem uma conta?
    router-link(to="/login") Faça login aqui!
</template>

<script>
import { api } from '@/services';

export default {
  name: 'CadastroPage',
  data() {
    return {
      cadastroForm: {
        name: '',
        email: '',
        password: ''
      }
    };
  },
  methods: {
    async cadastrar() {
      const { name, email, password } = this.cadastroForm;

      if (!name || !email || !password) {
        alert('Por favor, preencha todos os campos!');
        return;
      }

      try {
        const response = await api.createUser({ name, email, password });
        console.log('Usuário criado com sucesso', response);
        alert('Usuário cadastrado com sucesso! Faça login para continuar.');

        this.$router.push('/login');

      } catch (error) {
        console.error('Erro ao cadastrar usuário', error);
        alert(error.message || 'Erro ao cadastrar usuário!');
      }
    }
  }
};
</script>

<style lang="scss" scoped>
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

.cadastro-page {
  display: flex;
  flex-direction: column;
  width: 300px;
  height: auto;
  margin: 100px auto 0;
  padding: 20px;
  border-radius: 10px;
  background-color: $primary-blue;
  box-shadow: 0 5px 15px $shadow-color;
  border: none;

  h1 {
    text-align: center;
    margin-bottom: 20px;
    color: $text-light;
    font-weight: bold;
    font-size: 35px;
  }

  form {
    display: flex;
    flex-direction: column;
    margin: 0 auto;

    .form-group {
      display: flex;
      flex-direction: column;
      margin-bottom: 15px;
    }

    label {
      text-transform: capitalize;
      font-weight: 600;
      color: $text-light;
      margin-bottom: 5px;
    }

    input {
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

      &:focus {
        border: 2px solid $border-dark;
        background: $input-focus-bg;
        outline: none;
      }
    }

    .btn {
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

      &:hover {
        background: $button-hover-bg;
        color: $button-color;
      }
    }
  }

  p {
    text-align: center;
    margin-top: 20px;
    font-size: 0.9em;

    a {
      color: $link-color;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
        color: $link-hover-color;
      }
    }
  }
}
</style>