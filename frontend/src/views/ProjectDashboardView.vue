<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";
import api from "@/services/api";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const projects = ref<any[]>([]);
const selectedProjectId = ref<number | null>(null);
const loading = ref(true);

const kpis = ref([
  { title: "Budget Consommé", value: "0%", color: "text-blue-600", bg: "bg-blue-50" },
  { title: "Phases Terminées", value: "0/0", color: "text-green-600", bg: "bg-green-50" },
  { title: "Jours Restants", value: "0", color: "text-amber-600", bg: "bg-amber-50" },
  { title: "Tâches Ouvertes", value: "0", color: "text-red-600", bg: "bg-red-50" },
]);

const chartData = ref({
  labels: [] as string[],
  datasets: [
    {
      label: 'Dépenses (FCFA)',
      backgroundColor: '#d10f2f',
      data: [] as number[]
    }
  ]
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
};

const fetchProjects = async () => {
  try {
    const res = await api.get('/projects/');
    projects.value = res.data;
    if (projects.value.length > 0) {
      selectedProjectId.value = projects.value[0].id;
      await fetchDashboardData();
    } else {
      loading.value = false;
    }
  } catch (err) {
    console.error("Failed to fetch projects", err);
    loading.value = false;
  }
};

const fetchDashboardData = async () => {
  if (!selectedProjectId.value) return;
  loading.value = true;
  try {
    const res = await api.get(`/projects/${selectedProjectId.value}/dashboard`);
    kpis.value = res.data.kpis;
    chartData.value = {
      labels: res.data.financial_chart.labels,
      datasets: [
        {
          label: 'Dépenses (FCFA)',
          backgroundColor: '#d10f2f',
          data: res.data.financial_chart.data
        }
      ]
    };
  } catch (err) {
    console.error("Failed to fetch dashboard data", err);
  } finally {
    loading.value = false;
  }
};

watch(selectedProjectId, () => {
  fetchDashboardData();
});

onMounted(() => {
  fetchProjects();
});
</script>

<template>
  <div class="h-screen flex overflow-hidden">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Navbar />
      <main class="flex-1 overflow-y-auto bg-gray-50 p-8">
        <div class="max-w-7xl mx-auto space-y-8">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Dashboard Projet</h1>
              <p class="mt-1 text-gray-500">Suivi des KPIs, Budget et Avancement du Projet</p>
            </div>
            <div class="flex gap-4 items-center">
              <select v-model="selectedProjectId" class="px-4 py-2 rounded-lg border border-gray-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-[#d10f2f]">
                <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.code }} - {{ p.nom }}</option>
              </select>
              <button class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
                <span class="material-symbols-outlined text-sm">picture_as_pdf</span>
                Générer Rapport
              </button>
            </div>
          </div>

          <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

          <div v-else-if="!selectedProjectId" class="text-center py-12 text-gray-500">Aucun projet disponible.</div>

          <template v-else>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div v-for="kpi in kpis" :key="kpi.title" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div :class="[kpi.bg, kpi.color, 'w-12 h-12 rounded-lg flex items-center justify-center mb-4']">
                  <span class="material-symbols-outlined">analytics</span>
                </div>
                <p class="text-sm font-medium text-gray-500">{{ kpi.title }}</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">{{ kpi.value }}</p>
              </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-lg font-bold text-gray-900 mb-4">Dépenses Financières Annuelles</h2>
              <div class="h-80 w-full">
                <Bar :data="chartData" :options="chartOptions" />
              </div>
            </div>
          </template>
        </div>
      </main>
    </div>
  </div>
</template>
