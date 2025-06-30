<template>
  <div class="app-container">
    <NavBar></NavBar>
    <router-view></router-view>
  </div>
</template>

<script>
import NavBar from "@/components/NavBar.vue"

export default {
  name: "App", // Certifique-se de que o nome do componente é "App"
  components: { // Corrija "componente" para "components"
    NavBar
  }
}
</script>

<style>
/* Estilos gerais para o aplicativo podem ser adicionados aqui */
</style>
