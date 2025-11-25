<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Mapa de Rendimiento Académico</h1>

    <div class="bg-white p-6 shadow rounded-xl border">
      <apexchart
        type="heatmap"
        height="550"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ApexChart from "vue3-apexcharts";

// Registrar componente
const apexchart = ApexChart;

// --- MATERIAS ---
const materias = [
  "Matemática", "Lengua", "Inglés", "Historia", "Geografía",
  "Biología", "Química", "Física", "Arte", "Computación",
  "Educ. Física", "Música"
];

// --- GENERADOR DE 50 ALUMNOS (Nombres ficticios) ---
const alumnos = Array.from({ length: 50 }, (_, i) => `Alumno ${i + 1}`);

// --- GENERAR DATA ALEATORIA ---
function generarNotas() {
  return alumnos.map(() => Math.floor(Math.random() * 60) + 40); // 40–100
}

// --- SERIES PARA APEXCHART (materias como columnas) ---
const series = materias.map((materia, idx) => ({
  name: materia,
  data: generarNotas(), // 50 notas por materia (1 por alumno)
}));

// --- CONFIGURACIÓN DEL HEATMAP ---
const chartOptions = {
  chart: {
    toolbar: { show: true }
  },
  plotOptions: {
    heatmap: {
      shadeIntensity: 0.6,
      colorScale: {
        ranges: [
          { from: 0, to: 40, name: "Bajo", color: "#ef4444" },
          { from: 41, to: 60, name: "Regular", color: "#f59e0b" },
          { from: 61, to: 80, name: "Bueno", color: "#3b82f6" },
          { from: 81, to: 100, name: "Excelente", color: "#22c55e" },
        ]
      }
    }
  },
  dataLabels: {
    enabled: false
  },
  xaxis: {
    categories: alumnos, // 50 alumnos
  },
  legend: {
    position: "bottom"
  }
};
</script>
