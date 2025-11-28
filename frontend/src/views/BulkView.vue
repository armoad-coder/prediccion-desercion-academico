<template>
  <div class="p-8 bg-gray-50 min-h-screen">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">
      Carga Masiva de Datos Académicos
    </h1>
    <p class="text-gray-600 mb-8">
      Sube tu archivo CSV para actualizar masivamente los registros de alumnos y
      sus notas. Endpoint:
      <code class="bg-gray-200 p-1 rounded">/students/bulk_csv</code>.
    </p>

    <div
      class="max-w-xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-blue-200"
    >
      <div v-if="!loading && isSuccess === null">
        <h2 class="text-xl font-semibold mb-4 text-gray-700">
          1. Seleccionar archivo CSV
        </h2>

        <label
          for="csv-upload"
          class="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer transition"
          :class="{
            'border-blue-500 bg-blue-50 hover:bg-blue-100': !selectedFile,
            'border-green-600 bg-green-50': selectedFile,
          }"
        >
          <div v-if="selectedFile" class="text-center p-4">
            <svg
              class="w-10 h-10 text-green-500 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p class="mt-2 text-sm text-green-700 font-semibold">
              Archivo seleccionado:
            </p>
            <p class="text-base font-medium text-green-800">
              {{ selectedFile.name }} ({{
                (selectedFile.size / 1024).toFixed(1)
              }}
              KB)
            </p>

            <p v-if="localRecordCount > 0" class="text-xs text-gray-600 mt-1">
              Registros detectados:
              <span class="font-bold">{{ localRecordCount }}</span>
            </p>
          </div>

          <div v-else class="text-center p-4">
            <svg
              class="w-10 h-10 mb-3 text-blue-400 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 014 4v2a4 4 0 01-4 4h-4m-7 0l-4-4m4 4l4-4"
              />
            </svg>
            <p class="mb-2 text-sm text-gray-500">
              <span class="font-semibold">Click para subir</span> o arrastra y
              suelta
            </p>
            <p class="text-xs text-gray-500">Solo archivos CSV (máx. 10MB)</p>
          </div>

          <input
            id="csv-upload"
            type="file"
            class="hidden"
            @change="handleFileChange"
            accept=".csv"
          />
        </label>

        <div class="mt-6 flex justify-center">
          <button
            @click="uploadFile"
            :disabled="!selectedFile || localRecordCount === 0"
            class="px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700 transition disabled:opacity-50"
          >
            Iniciar Carga Masiva ({{ localRecordCount }} registros)
          </button>
        </div>
      </div>

      <div v-else-if="loading" class="text-center p-8">
        <h2 class="text-2xl font-bold truncate max-w-full text-gray-800 mb-6">
          Procesando {{ fileToUploadName }}...
        </h2>

        <div
          class="w-full bg-gray-200 rounded-full h-8 mb-4 overflow-hidden shadow-inner"
        >
          <div
            class="bg-blue-600 h-8 text-xs font-medium text-white text-center p-2 leading-none rounded-full transition-all duration-1000 ease-linear"
            :style="{ width: `${progressCount}%` }"
          >
            {{ progressCount.toFixed(0) }}%
          </div>
        </div>

        <p class="text-gray-600 text-lg">
          Registros cargados:
          <span class="font-extrabold text-blue-700">
            {{ simulatedRecordsProcessed }}
          </span>
          <span v-if="finalCountFromServer > 0" class="text-sm text-gray-500">
            / {{ finalCountFromServer }}
          </span>
        </p>

        <p class="mt-4 text-sm text-gray-500">
          Espere a que termine el registro.
        </p>
      </div>

      <div
        v-if="isSuccess !== null"
        class="mt-6 p-4 rounded-lg text-center"
        :class="{
          'bg-green-100 border border-green-400 text-green-700': isSuccess,
          'bg-red-100 border border-red-400 text-red-700': !isSuccess,
        }"
      >
        <p class="font-bold text-lg">
          {{ isSuccess ? "¡Carga Exitosa!" : "Error en la Carga" }}
        </p>
        <p class="text-sm mt-1">
          {{ isSuccess ? successMsg : errorMsg }}
          <button
            @click="resetForm"
            class="text-blue-600 hover:text-blue-800 font-semibold ml-2"
          >
            Volver a Cargar
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

const selectedFile = ref<File | null>(null);
const loading = ref(false);
const isSuccess = ref<boolean | null>(null);
const successMsg = ref("");
const errorMsg = ref("");

const localRecordCount = ref(0);
const progressCount = ref(0);
const recordsInterval = ref<any>(null);
const simulatedRecordsProcessed = ref(0);
const finalCountFromServer = ref(0);

const fileToUploadName = computed(() => selectedFile.value?.name || "Archivo");

// ----------------------------
// LEER CSV Y CONTAR REGISTROS
// ----------------------------
function countRecordsInFile(file: File) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target?.result as string;
    if (content) {
      const lines = content.trim().split(/\r\n|\r|\n/);
      localRecordCount.value = Math.max(0, lines.length - 1);
    } else {
      localRecordCount.value = 0;
    }
  };
  reader.onerror = () => {
    errorMsg.value = "Error al leer el archivo.";
    localRecordCount.value = 0;
  };
  reader.readAsText(file);
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = input.files;

  selectedFile.value = files && files.length > 0 ? files[0] : null;

  if (selectedFile.value) {
    countRecordsInFile(selectedFile.value);
  }
}

function resetForm() {
  selectedFile.value = null;
  loading.value = false;
  isSuccess.value = null;
  successMsg.value = "";
  errorMsg.value = "";
  progressCount.value = 0;
  simulatedRecordsProcessed.value = 0;
  finalCountFromServer.value = 0;
  localRecordCount.value = 0;
}

// ----------------------------
// ANIMACIÓN CONTROLADA
// ----------------------------
function startControlledAnimation(
  finalCount: number,
  success: boolean,
  message: string
) {
  finalCountFromServer.value = finalCount;

  if (finalCount === 0) {
    return stopAnimationImmediate(
      false,
      "El archivo no contiene registros válidos.",
      0
    );
  }

  const step = 100 / finalCount;
  let currentStep = 0;

  progressCount.value = 0;
  simulatedRecordsProcessed.value = 0;

  recordsInterval.value = setInterval(() => {
    simulatedRecordsProcessed.value++;
    currentStep += step;
    progressCount.value = Math.min(100, currentStep);

    if (simulatedRecordsProcessed.value >= finalCount) {
      clearInterval(recordsInterval.value);
      progressCount.value = 100;

      setTimeout(() => {
        loading.value = false;
        isSuccess.value = success;

        if (success) successMsg.value = message;
        else errorMsg.value = message;
      }, 250);
    }
  }, 150); // <-- intervalo ajustado
}

function stopAnimationImmediate(
  success: boolean,
  message: string,
  finalCount: number = 0
) {
  clearInterval(recordsInterval.value);
  loading.value = false;
  isSuccess.value = success;
  errorMsg.value = message;
  simulatedRecordsProcessed.value = finalCount;
  finalCountFromServer.value = finalCount;
  progressCount.value = success ? 100 : 0;
}

// ----------------------------
// UPLOAD ARCHIVO CSV
// ----------------------------
async function uploadFile() {
  if (!selectedFile.value || localRecordCount.value === 0) {
    errorMsg.value = "Seleccione un archivo válido con registros.";
    return;
  }

  loading.value = true;
  isSuccess.value = null;

  const countToAnimate = localRecordCount.value;

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  const ENDPOINT_URL = "http://127.0.0.1:5000/students/bulk_csv";

  startControlledAnimation(countToAnimate, true, "Procesando...");

  try {
    const response = await fetch(ENDPOINT_URL, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      const finalCount = result.records_processed || countToAnimate;
      successMsg.value =
        result.message || `${finalCount} registros procesados correctamente.`;
    } else {
      stopAnimationImmediate(
        false,
        result.error || `Error ${response.status}: Revise el CSV.`,
        simulatedRecordsProcessed.value
      );
    }
  } catch (err) {
    stopAnimationImmediate(
      false,
      "No se pudo conectar con el servidor Flask.",
      simulatedRecordsProcessed.value
    );
  }
}
</script>

<style scoped></style>
