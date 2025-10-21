<script setup lang="ts">
import Login from './components/Login.vue';
</script>

<template>
  <router-view />
  <Login />
</template>

<style scoped>
body, html {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
