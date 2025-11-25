<template>
  <div class="flex">
    <Sidebar />

    <main class="flex-1 p-6 bg-gray-100 min-h-screen">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from "@/components/layout/Sidebar.vue"
</script>
