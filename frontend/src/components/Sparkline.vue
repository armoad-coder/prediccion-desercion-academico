<template>
  <canvas ref="canvas" height="60"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Chart, LineController, LineElement, PointElement, LinearScale, CategoryScale } from "chart.js";

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale);

const canvas = ref<HTMLCanvasElement | null>(null);

onMounted(() => {
  if (!canvas.value) return;

  new Chart(canvas.value, {
    type: "line",
    data: {
      labels: ["1", "2", "3", "4", "5", "6"],
      datasets: [
        {
          data: [70, 75, 80, 78, 85, 90],
          borderColor: "#2563eb",
          backgroundColor: "transparent",
          borderWidth: 2,
          tension: 0.4,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { display: false },
      },
    },
  });
});
</script>
