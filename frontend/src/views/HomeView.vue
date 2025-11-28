<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Mapa de Rendimiento Académico</h1>

    <div class="flex flex-wrap items-center justify-between mb-6 gap-4">
      <div>
        <label class="font-semibold mr-3">Seleccionar semestre:</label>
        <select
          v-model="semestre"
          class="border rounded-lg px-3 py-2 shadow bg-white"
          @change="fetchData"
        >
          <option value="">-- Seleccionar --</option>
          <option value="1">1er Semestre</option>
          <option value="2">2do Semestre</option>
        </select>
      </div>

      <div
        v-if="rawSeries.length > 0"
        class="flex items-center gap-2 bg-white p-2 rounded-lg shadow border"
      >
        <button
          @click="prevPage"
          :disabled="currentPage === 1"
          class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 font-bold"
        >
          &lt;
        </button>

        <span class="text-sm font-semibold">
          Página {{ currentPage }} de {{ totalPages }}
        </span>

        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 font-bold"
        >
          &gt;
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-blue-500 font-semibold mb-4 animate-pulse">
      Cargando datos...
    </div>

    <div
      v-if="paginatedSeries.length > 0 && !loading"
      class="bg-white p-4 shadow rounded-xl border relative"
    >
      <apexchart
        key="heatmap-chart"
        type="heatmap"
        height="500"
        :options="chartOptions"
        :series="paginatedSeries"
      />
    </div>

    <div v-else-if="!loading" class="mt-10 text-gray-400 text-lg italic">
      Selecciona un semestre o no hay datos disponibles.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import ApexChart from "vue3-apexcharts";

// ----------------------------------------------------
// Configuración
// ----------------------------------------------------
const ITEMS_PER_PAGE = 15; // Muestra 15 alumnos por página para que se lea bien

// ----------------------------------------------------
// Estado
// ----------------------------------------------------
const semestre = ref("");
const rawSeries = ref([]); // Aquí guardamos TODOS los datos que vienen del servidor
const paginatedSeries = ref([]); // Aquí guardamos solo lo que se ve en la página actual
const loading = ref(false);

// Estado de paginación
const currentPage = ref(1);

// Calculamos el total de páginas basado en la cantidad de alumnos (data points)
const totalPages = computed(() => {
  if (rawSeries.value.length === 0) return 0;
  // Tomamos la primera materia para contar cuántos alumnos hay en total
  const totalStudents = rawSeries.value[0].data.length;
  return Math.ceil(totalStudents / ITEMS_PER_PAGE);
});

// ----------------------------------------------------
// Configuración del Gráfico
// ----------------------------------------------------
const chartOptions = reactive({
  chart: {
    toolbar: { show: false }, // Ocultamos toolbar para limpiar la vista
    animations: { enabled: false }, // Importante: Desactivar animación al paginar para que sea instantáneo
  },
  plotOptions: {
    heatmap: {
      shadeIntensity: 0.5,
      radius: 2, // Bordes un poco redondeados en los cuadros
      colorScale: {
        ranges: [
          { from: 1, to: 1, name: "1 (Muy Bajo)", color: "#FF0000" },
          { from: 2, to: 2, name: "2 (Bajo)", color: "#f97316" },
          { from: 3, to: 3, name: "3 (Medio)", color: "#eab308" },
          { from: 4, to: 4, name: "4 (Bueno)", color: "#3b82f6" },
          { from: 5, to: 5, name: "5 (Excelente)", color: "#22c55e" },
        ],
      },
    },
  },
  dataLabels: { enabled: false },
  xaxis: {
    type: "category",
    labels: {
      rotate: -45,
      trim: true,
      maxHeight: 100,
      style: { fontSize: "12px" },
    },
  },
  tooltip: {
    y: {
      formatter: (val: any) => (val === null ? "Sin Nota" : val),
    },
  },
});

// ----------------------------------------------------
// Lógica de Paginación
// ----------------------------------------------------
function updatePaginatedData() {
  if (rawSeries.value.length === 0) {
    paginatedSeries.value = [];
    return;
  }

  const start = (currentPage.value - 1) * ITEMS_PER_PAGE;
  const end = start + ITEMS_PER_PAGE;

  // Recorremos cada materia (serie) y cortamos el array de alumnos (data)
  paginatedSeries.value = rawSeries.value.map((serie: any) => ({
    name: serie.name,
    data: serie.data.slice(start, end),
  }));
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    updatePaginatedData();
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    updatePaginatedData();
  }
}

// ----------------------------------------------------
// Carga de Datos
// ----------------------------------------------------
async function fetchData() {
  if (!semestre.value) {
    rawSeries.value = [];
    paginatedSeries.value = [];
    return;
  }

  loading.value = true;
  // Reiniciamos a la página 1 cuando cambiamos de semestre
  currentPage.value = 1;

  try {
    // ⚠️ Ajusta tu URL aquí
    const response = await fetch(
      `http://127.0.0.1:5000/api/heatmap-data?semestre=${semestre.value}`
    );
    if (!response.ok) throw new Error("Error en la petición");

    const data = await response.json();

    // Guardamos la data completa en rawSeries
    rawSeries.value = data;

    // Ejecutamos el corte inicial para mostrar la página 1
    updatePaginatedData();
  } catch (error) {
    console.error("Error:", error);
    rawSeries.value = [];
  } finally {
    loading.value = false;
  }
}
</script>
