<template>
  <div class="p-6 space-y-6">

    <!-- TITULO -->
    <h1 class="text-2xl font-bold text-gray-800">
      Panel Académico
    </h1>

    <!-- TARJETAS KPI -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

      <div class="bg-white p-5 shadow rounded-xl border">
        <p class="text-gray-500">Total Alumnos</p>
        <h2 class="text-3xl font-bold">{{ stats.alumnos }}</h2>
      </div>

      <div class="bg-white p-5 shadow rounded-xl border">
        <p class="text-gray-500">Materias Activas</p>
        <h2 class="text-3xl font-bold">{{ stats.materias }}</h2>
      </div>

      <div class="bg-white p-5 shadow rounded-xl border">
        <p class="text-gray-500">Promedio General</p>
        <h2 class="text-3xl font-bold">{{ stats.promedio }}%</h2>
      </div>

      <div class="bg-white p-5 shadow rounded-xl border">
        <p class="text-gray-500">Alumnos en Riesgo</p>
        <h2 class="text-3xl font-bold">{{ stats.riesgo }}</h2>
      </div>

    </div>

    <!-- GRAFICOS -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- GRAFICO NOTAS -->
      <div class="bg-white p-5 shadow rounded-xl border">
        <h3 class="text-lg font-semibold mb-2">Promedio por Materia</h3>
        <apexchart type="bar" height="300" :options="chartNotas.options" :series="chartNotas.series" />
      </div>

      <!-- GRAFICO ASISTENCIAS -->
      <div class="bg-white p-5 shadow rounded-xl border">
        <h3 class="text-lg font-semibold mb-2">Asistencias del Mes</h3>
        <apexchart type="area" height="300" :options="chartAsist.options" :series="chartAsist.series" />
      </div>

    </div>

    <!-- TABLA RESUMEN -->
    <div class="bg-white p-5 shadow rounded-xl border">
      <h3 class="text-lg font-semibold mb-3">Alumnos con Bajo Rendimiento</h3>

      <table class="w-full border-collapse">
        <thead>
          <tr class="text-left border-b">
            <th class="py-2">Alumno</th>
            <th class="py-2">Materia</th>
            <th class="py-2">Promedio</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(a, i) in riesgoList" :key="i" class="border-b">
            <td class="py-2">{{ a.nombre }}</td>
            <td>{{ a.materia }}</td>
            <td class="text-red-600 font-semibold">{{ a.promedio }}%</td>
          </tr>
        </tbody>
      </table>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ApexChart from "vue3-apexcharts";

// Registro del componente
const apexchart = ApexChart;

// KPI
const stats = ref({
  alumnos: 350,
  materias: 42,
  promedio: 78,
  riesgo: 12
});

// Datos del gráfico de notas
const chartNotas = {
  options: {
    chart: { toolbar: { show: false } },
    xaxis: {
      categories: ["Matemática", "Inglés", "Historia", "Biología", "Computación"]
    }
  },
  series: [
    {
      name: "Promedio",
      data: [70, 82, 75, 68, 90]
    }
  ]
};

// Datos del gráfico de asistencias
const chartAsist = {
  options: {
    chart: { toolbar: { show: false } },
    xaxis: { categories: ["Lun", "Mar", "Mié", "Jue", "Vie"] }
  },
  series: [
    {
      name: "Asistencias",
      data: [120, 140, 130, 150, 160]
    }
  ]
};

// Tabla alumnos en riesgo
const riesgoList = ref([
  { nombre: "Juan Pérez", materia: "Matemática", promedio: 45 },
  { nombre: "Ana López", materia: "Inglés", promedio: 50 },
  { nombre: "Carlos Gómez", materia: "Historia", promedio: 48 }
]);
</script>

<style scoped>
/* opcional si quieres suavizar sombras */
</style>
