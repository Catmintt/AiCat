<!-- src/components/CatLogo.vue -->
<template>
  <svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <!-- Cat face shape -->
    <path d="M 50,95 C 20,95 5,70 5,40 C 5,10 20,5 50,5 C 80,5 95,10 95,40 C 95,70 80,95 50,95 Z" fill="#7B61FF"/>
    
    <!-- Ears -->
    <path d="M 15,35 L 15,15 L 35,20 Z" fill="#FFFFFF" />
    <path d="M 85,35 L 85,15 L 65,20 Z" fill="#FFFFFF" />

    <!-- Eyes -->
    <circle cx="35" cy="50" r="7" fill="#FFFFFF"/>
    <circle cx="65" cy="50" r="7" fill="#FFFFFF"/>
    
    <!-- Nose -->
    <path d="M 50,65 L 45,75 L 55,75 Z" fill="#FFFFFF"/>
  </svg>
</template>

<script setup lang="ts">
// This is a simple SVG component, no script logic is needed.
</script>