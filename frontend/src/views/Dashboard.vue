<template>
  <div class="min-h-screen bg-gray-50 p-6 font-sans">
    <div class="max-w-4xl mx-auto mb-10">
      <div
        class="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 text-center"
      >
        <h2 class="text-xl font-bold text-gray-700 mb-4">
          Sistema de Predicción de Deserción Académica
        </h2>

        <div class="flex flex-col gap-3 items-center">
          <div class="flex gap-3 w-full justify-center">
            <input
              v-model="busquedaCedula"
              type="text"
              placeholder="Ingrese Cédula del Alumno (Ej: 5375)"
              class="w-full max-w-md px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
              @keyup.enter="buscarAlumno"
            />
            <button
              @click="buscarAlumno"
              :disabled="loading || !busquedaCedula"
              class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <span v-if="loading" class="flex items-center">
                <svg
                  class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Procesando...
              </span>
              <span v-else>Consultar IA</span>
            </button>
          </div>

          <p
            v-if="errorMsg"
            class="text-red-500 font-semibold mt-2 animate-bounce"
          >
            ⚠️ {{ errorMsg }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div
        class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600 mb-4"
      ></div>
      <p class="text-gray-500 text-lg animate-pulse">
        Consultando historial y generando predicción...
      </p>
    </div>

    <div v-else-if="!studentData" class="text-center py-20 opacity-50">
      <div class="text-6xl mb-4">🎓</div>
      <p class="text-xl text-gray-400">
        Ingrese una cédula para ver el reporte detallado.
      </p>
    </div>

    <div v-else class="space-y-6 animate-fade-in-up">
      <div
        class="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-6 rounded-xl shadow border"
      >
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            Reporte: {{ studentData.alumno.nombre }}
            {{ studentData.alumno.apellido }}
          </h1>
          <p class="text-sm text-gray-500 mt-1">
            Cédula: {{ studentData.alumno.cedula }} | ID Interno:
            {{ studentData.alumno.id }}
          </p>
        </div>
        <div
          class="mt-4 md:mt-0 px-6 py-2 rounded-full font-bold text-white shadow-md tracking-wide uppercase text-sm"
          :class="badgeColor"
        >
          {{ studentData.prediccion.descripcion }}
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white p-5 shadow rounded-xl border-l-4 border-green-500">
          <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">
            Probabilidad Éxito
          </p>
          <h2 class="text-3xl font-bold text-gray-800 mt-1">
            {{ (studentData.prediccion.probabilidades["2"] * 100).toFixed(2) }}%
          </h2>
        </div>
        <div class="bg-white p-5 shadow rounded-xl border-l-4 border-blue-500">
          <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">
            Promedio General
          </p>
          <h2 class="text-3xl font-bold text-gray-800 mt-1">
            {{ studentData.alumno.promedio.toFixed(2) }}
          </h2>
        </div>
        <div
          class="bg-white p-5 shadow rounded-xl border-l-4 border-purple-500"
        >
          <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">
            Tiempo de Estudio
          </p>
          <h2 class="text-3xl font-bold text-gray-800 mt-1">
            {{ studentData.alumno.tiempo_estudio }}/5
          </h2>
        </div>
        <div class="bg-white p-5 shadow rounded-xl border-l-4 border-red-500">
          <p class="text-gray-500 text-xs font-bold uppercase tracking-wider">
            Total Ausencias
          </p>
          <h2 class="text-3xl font-bold text-gray-800 mt-1">
            {{ studentData.alumno.ausencias }}
          </h2>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white p-6 shadow rounded-xl border lg:col-span-1">
          <h3 class="text-lg font-bold text-gray-700 mb-2 text-center">
            Perfil Integral
          </h3>
          <apexchart
            type="radar"
            height="300"
            :options="chartRadar.options"
            :series="chartRadar.series"
          />
          <p class="text-xs text-gray-400 text-center">
            Comparativa: Alumno (Azul) vs. Ideal (Verde)
          </p>
        </div>

        <div
          class="bg-white p-6 shadow rounded-xl border lg:col-span-2 flex flex-col"
        >
          <h3 class="text-lg font-bold text-gray-700 mb-4 border-b pb-2">
            Diagnóstico y Recomendaciones
          </h3>

          <div class="flex-1 space-y-4">
            <div class="bg-blue-50 border-l-4 border-blue-600 p-3 rounded">
              <h4 class="text-sm font-bold text-blue-800">
                Interpretación del Modelo:
              </h4>
              <p class="text-sm text-blue-700 mt-1 whitespace-pre-line">
                {{ studentData.prediccion.texto }}
              </p>
            </div>

            <div>
              <h4 class="text-sm font-bold text-gray-700 mb-2">
                Acciones Sugeridas:
              </h4>
              <ul class="space-y-2">
                <li
                  v-for="(rec, index) in recomendaciones"
                  :key="index"
                  class="flex items-start text-sm bg-gray-50 p-2 rounded border hover:bg-gray-100 transition"
                >
                  <span class="mr-3 text-xl">{{ rec.icono }}</span>
                  <div>
                    <strong class="block text-gray-800">{{
                      rec.titulo
                    }}</strong>
                    <span class="text-gray-600">{{ rec.desc }}</span>
                  </div>
                </li>
              </ul>
              <div
                v-if="recomendaciones.length === 0"
                class="text-center py-4 text-green-600"
              >
                <span class="text-2xl">✨</span>
                <p class="text-sm font-semibold">
                  Desempeño óptimo. No se requieren acciones correctivas.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-6 shadow rounded-xl border">
          <h3 class="text-lg font-bold text-gray-700 mb-4 border-b pb-2">
            Desglose de Probabilidades
          </h3>
          <apexchart
            type="donut"
            height="300"
            :options="chartProb.options"
            :series="chartProb.series"
          />
        </div>
        <div class="bg-white p-6 shadow rounded-xl border">
          <h3 class="text-lg font-bold text-gray-700 mb-4 border-b pb-2">
            Top 10 Materias con Menor Nota
          </h3>
          <apexchart
            type="bar"
            height="300"
            :options="chartMaterias.options"
            :series="chartMaterias.series"
          />
        </div>
      </div>

      <div class="bg-white shadow rounded-xl border overflow-hidden">
        <div class="px-6 py-4 border-b bg-gray-50">
          <h3 class="text-lg font-bold text-gray-700">
            Historial Académico Completo
          </h3>
        </div>
        <div class="max-h-96 overflow-y-auto">
          <table class="w-full text-sm text-left">
            <thead
              class="text-xs text-gray-700 uppercase bg-gray-100 sticky top-0"
            >
              <tr>
                <th class="px-6 py-3">Materia</th>
                <th class="px-6 py-3 text-right">Nota</th>
                <th class="px-6 py-3 text-center">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(nota, materia) in studentData.materias"
                :key="materia"
                class="bg-white border-b hover:bg-gray-50"
              >
                <td class="px-6 py-3 font-medium text-gray-900">
                  {{ materia }}
                </td>
                <td
                  class="px-6 py-3 text-right font-bold font-mono"
                  :class="getColorNota(nota)"
                >
                  {{ nota }}
                </td>
                <td class="px-6 py-3 text-center">
                  <span
                    class="px-2 py-1 rounded-full text-xs font-semibold border"
                    :class="
                      nota >= 2
                        ? 'bg-green-50 text-green-700 border-green-200'
                        : 'bg-red-50 text-red-700 border-red-200'
                    "
                  >
                    {{ nota >= 2 ? "Aprobado" : "Reprobado" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import ApexChart from "vue3-apexcharts";

// --------------------------------------------------------
// ESTADO
// --------------------------------------------------------
const busquedaCedula = ref("");
const loading = ref(false);
const errorMsg = ref("");
const studentData = ref(null);

// --------------------------------------------------------
// LÓGICA API (CONEXIÓN FLASK)
// --------------------------------------------------------
async function buscarAlumno() {
  if (!busquedaCedula.value) return;

  loading.value = true;
  studentData.value = null;
  errorMsg.value = "";

  try {
    // LLAMADA REAL A TU ENDPOINT
    const response = await fetch(
      `http://127.0.0.1:5000/predict/${busquedaCedula.value}`
    );

    if (!response.ok) {
      if (response.status === 404) throw new Error("Alumno no encontrado.");
      if (response.status === 500) throw new Error("Error del servidor.");
      throw new Error(`Error HTTP: ${response.status}`);
    }

    const data = await response.json();
    studentData.value = data;
  } catch (error: any) {
    console.error("Error:", error);
    errorMsg.value = error.message || "Error de conexión.";
  } finally {
    loading.value = false;
  }
}

// --------------------------------------------------------
// GRÁFICOS Y LÓGICA (COMPUTED)
// --------------------------------------------------------

// 1. DONUT: PROBABILIDADES
const chartProb = computed(() => {
  if (!studentData.value) return { series: [], options: {} };
  const probs = studentData.value.prediccion.probabilidades;
  return {
    series: [probs["2"], probs["3"], probs["4"]],
    options: {
      labels: ["Graduado", "Deserción Temprana", "Deserción Tardía"],
      colors: ["#22c55e", "#ef4444", "#f97316"],
      plotOptions: {
        pie: {
          donut: {
            size: "65%",
            labels: {
              show: true,
              total: {
                show: true,
                label: "Confianza",
                formatter: () => (probs["2"] * 100).toFixed(1) + "%",
              },
            },
          },
        },
      },
      legend: { position: "bottom" },
      dataLabels: { enabled: false },
    },
  };
});

// 2. BARRAS: MATERIAS CRÍTICAS (BOTTOM 10)
const chartMaterias = computed(() => {
  if (!studentData.value) return { series: [], options: {} };
  const lista = Object.entries(studentData.value.materias)
    .map(([nombre, nota]) => ({ nombre, nota: Number(nota) }))
    .sort((a, b) => a.nota - b.nota)
    .slice(0, 10);

  return {
    series: [{ name: "Nota", data: lista.map((i) => i.nota) }],
    options: {
      chart: { toolbar: { show: false } },
      colors: ["#3b82f6"],
      plotOptions: {
        bar: { horizontal: true, borderRadius: 4, barHeight: "70%" },
      },
      xaxis: { categories: lista.map((i) => i.nombre), max: 5 },
      dataLabels: { enabled: true, offsetX: -6 },
    },
  };
});

// 3. RADAR: PERFIL VS IDEAL (TESIS)
const chartRadar = computed(() => {
  if (!studentData.value) return { series: [], options: {} };
  const al = studentData.value.alumno;

  // Normalización a escala 0-100
  const promedioScore = (al.promedio / 5) * 100;
  const estudioScore = (al.tiempo_estudio / 5) * 100;
  const asistenciaScore = Math.max(0, 100 - al.ausencias * 5); // 20 ausencias = 0
  const regularidadScore = Math.max(0, 100 - al.cinco_F * 20); // 5 materias con 1 = 0

  return {
    series: [
      {
        name: "Alumno Actual",
        data: [promedioScore, estudioScore, asistenciaScore, regularidadScore],
      },
      { name: "Perfil Ideal", data: [100, 100, 100, 100] },
    ],
    options: {
      chart: { toolbar: { show: false } },
      labels: ["Promedio", "Hábitos Estudio", "Asistencia", "Regularidad"],
      colors: ["#3b82f6", "#22c55e"],
      stroke: { width: 2 },
      fill: { opacity: 0.2 },
      markers: { size: 4 },
      yaxis: { show: false, max: 100 },
    },
  };
});

// 4. GENERADOR DE RECOMENDACIONES (LÓGICA DE NEGOCIO)
const recomendaciones = computed(() => {
  if (!studentData.value) return [];
  const list = [];
  const al = studentData.value.alumno;

  if (al.promedio < 3)
    list.push({
      icono: "📚",
      titulo: "Refuerzo Académico",
      desc: "Promedio crítico. Se sugiere tutoría par.",
    });
  else if (al.promedio < 3.5)
    list.push({
      icono: "📝",
      titulo: "Monitoreo",
      desc: "Promedio en el límite. Revisar evolución.",
    });

  if (al.tiempo_estudio <= 2)
    list.push({
      icono: "🧠",
      titulo: "Hábitos de Estudio",
      desc: "Baja dedicación. Sugerir taller de gestión de tiempo.",
    });
  if (al.ausencias > 10)
    list.push({
      icono: "⚠️",
      titulo: "Alerta Asistencia",
      desc: "Ausentismo alto. Contactar a bienestar estudiantil.",
    });
  if (al.cinco_F > 0)
    list.push({
      icono: "📉",
      titulo: "Riesgo Recursado",
      desc: `Tiene ${al.cinco_F} materias reprobadas con 1.`,
    });

  // Riesgo Deserción > 30%
  const riesgo =
    (studentData.value.prediccion.probabilidades["3"] || 0) +
    (studentData.value.prediccion.probabilidades["4"] || 0);
  if (riesgo > 0.3)
    list.push({
      icono: "🚨",
      titulo: "INTERVENCIÓN PRIORITARIA",
      desc: "Alto riesgo de deserción detectado por IA.",
    });

  return list;
});

// --------------------------------------------------------
// UTILIDADES VISUALES
// --------------------------------------------------------
const badgeColor = computed(() => {
  if (!studentData.value) return "";
  return studentData.value.prediccion.estado === 2
    ? "bg-green-500"
    : "bg-red-500";
});

function getColorNota(nota: number) {
  if (nota === 5) return "text-green-600";
  if (nota >= 3) return "text-blue-600";
  if (nota >= 2) return "text-orange-500";
  return "text-red-600";
}
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}
</style>
