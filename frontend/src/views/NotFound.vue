<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
    
    <!-- Círculo con icono -->
    <div class="bg-blue-700 text-white w-28 h-28 flex items-center justify-center rounded-full shadow-lg mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 9v2m0 4h.01M12 5c-7.732 0-14 3.134-14 7s6.268 7 14 7 14-3.134 14-7-6.268-7-14-7z" />
      </svg>
    </div>

    <!-- Título -->
    <h1 class="text-6xl font-extrabold text-gray-800 mb-2">404</h1>

    <!-- Subtítulo -->
    <p class="text-lg text-gray-600 mb-6 text-center max-w-md">
      La página que estás buscando no existe o fue movida.
    </p>

    <!-- Botones -->
    <div class="flex gap-4">
      <router-link
        to="/home"
        class="px-5 py-2 bg-blue-700 text-white rounded-lg shadow hover:bg-blue-800 transition font-semibold"
      >
        Ir al Inicio
      </router-link>
    </div>

  </div>
</template>

<script setup>
</script>
