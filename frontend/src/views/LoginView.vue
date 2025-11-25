<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-200">
    <div class="w-full max-w-sm bg-white p-8 rounded-lg shadow-lg border border-gray-300">

      <!-- LOGO -->
      <img src="/logo_fct.png" class="mx-auto mb-4 w-48 object-contain" />

      <!-- TITULO -->
      <h2 class="text-xl font-bold text-gray-700 mb-6 text-center">
        Iniciar Sesión
      </h2>

      <!-- FORM -->
      <form @submit.prevent="login">

        <!-- Usuario -->
        <div class="mb-4">
          <label class="block text-gray-600 font-medium mb-1">Usuario</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-3 py-2 border border-gray-400 rounded focus:ring-blue-600 focus:border-blue-600"
            placeholder="Ingresa tu usuario"
          />
        </div>

        <!-- Contraseña -->
        <div class="mb-5">
          <label class="block text-gray-600 font-medium mb-1">Contraseña</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-3 py-2 border border-gray-400 rounded focus:ring-blue-600 focus:border-blue-600"
            placeholder="Ingresa tu contraseña"
          />
        </div>
        <transition name="fade">
          <div
            v-if="errorMessage"
            class="mb-4 px-4 py-3 bg-red-600 text-white rounded shadow-md text-sm font-medium"
          >
            {{ errorMessage }}
          </div>
        </transition>
        <!-- Botón -->
        <button
          type="submit"
          class="w-full bg-blue-700 text-white py-2 rounded-md hover:bg-blue-800 transition font-semibold shadow"
        >
          Ingresar
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/stores/userStore";
import { useRouter } from "vue-router";
import Swal from "sweetalert2";

const username = ref("");
const password = ref("");
const errorMessage = ref("");


const userStore = useUserStore();
const router = useRouter();

const login = async () => {
  const ok = await userStore.login(username.value, password.value);

  if (ok) {
    await Swal.fire({
      title: "Bienvenido",
      text: "Inicio de sesión exitoso",
      icon: "success",
      timer: 2000,                 // ⏳ 2 segundos
      showConfirmButton: false,    // 🚫 Oculta botón
      timerProgressBar: true,      // 📊 Barra de progreso
    });

    router.push("/home");           // 👉 Recién aquí pasa de página
  } else {
    Swal.fire({
      title: "Error",
      text: "Usuario o contraseña incorrectos",
      icon: "error",
      confirmButtonColor: "#d33",
    });
  }
};

</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>