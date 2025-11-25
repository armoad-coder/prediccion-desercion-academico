<template>
  <div class="p-6">

    <!-- Card Mejorado -->
    <div
      @click="openModal = true"
      class="cursor-pointer bg-white border rounded-xl shadow-md hover:shadow-xl 
             p-6 transition w-72 group"
    >
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-lg font-semibold text-gray-700 group-hover:text-blue-700">
          Primer Semestre
        </h2>
        <span class="text-blue-600 text-sm font-medium bg-blue-100 px-2 py-1 rounded">
          2024
        </span>
      </div>

      <!-- Mini Gráfico -->
      <Sparkline />

      <p class="mt-3 text-gray-500 text-sm">
        Resumen de desempeño académico del semestre.
      </p>
    </div>

    <!-- Modal Heatmap -->
    <!-- Modal Heatmap -->
<TransitionRoot appear :show="openModal" as="template">
  <Dialog
    as="div"
    class="fixed inset-0 z-50 overflow-y-auto"
    @close="openModal = false"
  >
    
    <!-- Background overlay -->
    <TransitionChild
      as="template"
      enter="ease-out duration-300"
      enter-from="opacity-0"
      enter-to="opacity-100"
      leave="ease-in duration-200"
      leave-from="opacity-100"
      leave-to="opacity-0"
    >
      <div class="fixed inset-0 bg-black/40" />
    </TransitionChild>

    <!-- Modal container -->
    <div class="flex min-h-full items-center justify-center p-4 text-center">

      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0 scale-95"
        enter-to="opacity-100 scale-100"
        leave="ease-in duration-200"
        leave-from="opacity-100 scale-100"
        leave-to="opacity-0 scale-95"
      >
        <DialogPanel
          class="
            w-full 
            max-w-5xl 
            transform 
            overflow-hidden 
            rounded-2xl 
            bg-white 
            p-6 
            text-left 
            align-middle 
            shadow-xl 
            transition-all
            max-h-[90vh]
          "
        >
          <DialogTitle class="text-xl font-semibold mb-4">
            Heatmap Alumnos vs Materias
          </DialogTitle>

          <!-- Scroll interno si el contenido es grande -->
          <div class="overflow-auto max-h-[70vh]">
            <Heatmap />
          </div>

          <div class="mt-6 flex justify-end">
            <button
              @click="openModal = false"
              class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
            >
              Cerrar
            </button>
          </div>
        </DialogPanel>
      </TransitionChild>
    </div>
  </Dialog>
</TransitionRoot>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Heatmap from "@/components/Heatmap.vue";
import Sparkline from "@/components/Sparkline.vue";

// Modal flag
const openModal = ref(false);

// HeadlessUI imports
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot,
  TransitionChild,
} from "@headlessui/vue";
</script>
