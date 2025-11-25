<template>
  <aside class="w-64 bg-[#41403b] text-white h-screen shadow-xl flex flex-col select-none">

    <!-- LOGO / TÍTULO -->
    <div class="p-4 text-center border-b border-gray-600">
      <h1 class="text-xl font-bold">FCT – UNCA</h1>
    </div>

    <!-- MENU -->
    <nav class="flex-1 overflow-y-auto">
      <ul class="mt-4">

        <!-- INICIO -->
        <li>
          <router-link
            to="/home"
            class="flex items-center px-4 py-2 hover:bg-[#57544f] transition rounded"
          >
            <span class="material-icons mr-3">home</span>
            Inicio
          </router-link>
        </li>

        <!-- DASHBOARD -->
        <li>
          <router-link
            to="/dashboard"
            class="flex items-center px-4 py-2 hover:bg-[#57544f] transition rounded"
          >
            <span class="material-icons mr-3">dashboard</span>
            Dashboard
          </router-link>
        </li>

        <!-- CONFIGURACIÓN (submenu estilo AdminLTE) -->
        <li>
          <button
            @click="toggleConfig"
            class="flex items-center justify-between w-full px-4 py-2 hover:bg-[#57544f] transition rounded"
          >
            <div class="flex items-center">
              <span class="material-icons mr-3">settings</span>
              Configuración
            </div>

            <!-- Flecha -->
            <svg
              class="w-4 h-4 transform transition"
              :class="{ 'rotate-90': configOpen }"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <!-- SUBMENÚ -->
          <transition name="slide-fade">
            <ul
              v-if="configOpen"
              class="ml-10 mt-1 space-y-1 text-sm border-l border-gray-600 pl-4"
            >
              <li>
                <router-link
                  to="/config/usuarios"
                  class="block px-2 py-1 hover:text-gray-300"
                >
                  Usuarios
                </router-link>
              </li>

              <li>
                <router-link
                  to="/config/alumnos"
                  class="block px-2 py-1 hover:text-gray-300"
                >
                  Alumnos
                </router-link>
              </li>

              <!-- Cerrar sesión -->
              <li>
                <button
                  @click="logout"
                  class="w-full text-left px-4 py-2 rounded transition"
                >
                  Cerrar sesión
                </button>
              </li>
            </ul>
          </transition>
        </li>

      </ul>
    </nav>

  </aside>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/userStore";

const userStore = useUserStore();
const router = useRouter();
const configOpen = ref(false);

function toggleConfig() {
  configOpen.value = !configOpen.value;
}
const logout = () => {
  userStore.logout();
  router.push("/login");
};
</script>

<style scoped>
/* Animación del submenú */
.slide-fade-enter-active {
  transition: all 0.25s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.25s ease-in;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
