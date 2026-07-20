<script setup lang="ts">
import { ref, onMounted } from "vue";
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";

import api from '../services/api';

const kpis = ref([
  { title: "Projets Actifs", value: "0", icon: "work", color: "text-blue-600", bg: "bg-blue-50" },
  { title: "Employés", value: "0", icon: "people", color: "text-green-600", bg: "bg-green-50" },
  { title: "Demandes en attente", value: "0", icon: "assignment_late", color: "text-amber-600", bg: "bg-amber-50" },
  { title: "Alertes Stock", value: "0", icon: "warning", color: "text-red-600", bg: "bg-red-50" },
]);

const recentActivity = ref<any[]>([
  { id: 1, action: "Chargement des activités récentes...", time: "", icon: "sync" }
]);

const activeModal = ref<'project' | 'hr' | 'fuel' | null>(null);

const projectForm = ref({ code: '', nom: '', date_debut_estimee: '', date_fin_estimee: '' });
const hrForm = ref({ request_type: '', description: '' });
const fuelForm = ref({ vehicle_plate: '', fuel_type: '', amount: null, justification: '' });

const refreshDashboard = async () => {
  try {
    const kpiRes = await api.get('/dashboard/kpis');
    const data = kpiRes.data;
    if (kpis.value[0]) kpis.value[0].value = data.active_projects.toString();
    if (kpis.value[1]) kpis.value[1].value = data.employees.toString();
    if (kpis.value[2]) kpis.value[2].value = data.pending_requests.toString();
    if (kpis.value[3]) kpis.value[3].value = data.stock_alerts.toString();
    
    const activityRes = await api.get('/dashboard/recent-activity');
    recentActivity.value = activityRes.data;
  } catch (error) {
    console.error("Failed to load dashboard data", error);
  }
};

const createProject = async () => {
  try {
    await api.post('/projects/', projectForm.value);
    activeModal.value = null;
    alert('Projet créé avec succès !');
    projectForm.value = { code: '', nom: '', date_debut_estimee: '', date_fin_estimee: '' };
    await refreshDashboard();
  } catch (err) {
    alert('Erreur lors de la création du projet');
  }
};

const createHRRequest = async () => {
  try {
    await api.post('/hr-requests/', {
      ...hrForm.value,
      employee_id: 1 // Default demo employee
    });
    activeModal.value = null;
    alert('Demande RH créée !');
    hrForm.value = { request_type: '', description: '' };
    await refreshDashboard();
  } catch (err) {
    alert('Erreur création demande RH');
  }
};

const createFuelRequest = async () => {
  try {
    await api.post('/fuel-requests/', fuelForm.value);
    activeModal.value = null;
    alert('Demande Carburant créée !');
    fuelForm.value = { vehicle_plate: '', fuel_type: '', amount: null, justification: '' };
    await refreshDashboard();
  } catch(err) {
    alert('Erreur création demande carburant');
  }
};

onMounted(async () => {
  await refreshDashboard();
});
</script>

<template>
  <div class="h-screen flex overflow-hidden">
    <Sidebar />

    <div class="flex-1 flex flex-col">
      <Navbar />

      <main class="flex-1 overflow-y-auto bg-gray-50 p-8">
        <div class="max-w-7xl mx-auto space-y-8">
          
          <!-- Header -->
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Tableau de bord</h1>
              <p class="mt-1 text-gray-500">Aperçu général des activités COSELEC</p>
            </div>
            <button class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
              <span class="material-symbols-outlined text-sm">download</span>
              Rapport
            </button>
          </div>

          <!-- KPI Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div v-for="kpi in kpis" :key="kpi.title" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-start gap-4">
              <div :class="[kpi.bg, kpi.color, 'p-3 rounded-lg']">
                <span class="material-symbols-outlined text-3xl">{{ kpi.icon }}</span>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-500">{{ kpi.title }}</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">{{ kpi.value }}</p>
              </div>
            </div>
          </div>

          <!-- Content Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Quick Actions -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 lg:col-span-2">
              <h2 class="text-lg font-bold text-gray-900 mb-4">Actions Rapides</h2>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <button @click="activeModal = 'project'" class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <span class="material-symbols-outlined text-[#d10f2f] mb-2">add_circle</span>
                  <span class="text-sm font-medium text-gray-700">Nouveau Projet</span>
                </button>
                <button @click="activeModal = 'hr'" class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <span class="material-symbols-outlined text-[#d10f2f] mb-2">post_add</span>
                  <span class="text-sm font-medium text-gray-700">Demande RH</span>
                </button>
                <router-link to="/stock/movement" class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <span class="material-symbols-outlined text-[#d10f2f] mb-2">sync_alt</span>
                  <span class="text-sm font-medium text-gray-700">Mouvement Stock</span>
                </router-link>
                <button @click="activeModal = 'fuel'" class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <span class="material-symbols-outlined text-[#d10f2f] mb-2">directions_car</span>
                  <span class="text-sm font-medium text-gray-700">Demande Carburant</span>
                </button>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 class="text-lg font-bold text-gray-900 mb-4">Activité Récente</h2>
              <ul class="space-y-4">
                <li v-for="act in recentActivity" :key="act.id" class="flex items-start gap-3">
                  <div class="bg-gray-50 p-2 rounded-full mt-1">
                    <span class="material-symbols-outlined text-sm text-gray-600">{{ act.icon }}</span>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ act.action }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ act.time }}</p>
                  </div>
                </li>
              </ul>
            </div>

          </div>

        </div>
      </main>

      <!-- MODALS -->
      <div v-if="activeModal === 'project'" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-xl w-96 shadow-xl">
          <h2 class="text-xl font-bold mb-4 text-gray-900">Nouveau Projet</h2>
          <form @submit.prevent="createProject" class="space-y-3">
            <input v-model="projectForm.code" placeholder="Code (ex: PRJ-01)" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            <input v-model="projectForm.nom" placeholder="Nom du projet" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            <div>
              <label class="block text-xs text-gray-500 mb-1">Date début estimée</label>
              <input type="date" v-model="projectForm.date_debut_estimee" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Date fin estimée</label>
              <input type="date" v-model="projectForm.date_fin_estimee" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            </div>
            <div class="flex justify-end gap-2 mt-4">
              <button type="button" @click="activeModal = null" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
              <button type="submit" class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg">Créer</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="activeModal === 'hr'" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-xl w-96 shadow-xl">
          <h2 class="text-xl font-bold mb-4 text-gray-900">Nouvelle Demande RH</h2>
          <form @submit.prevent="createHRRequest" class="space-y-3">
            <select v-model="hrForm.request_type" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500">
              <option value="" disabled>Type de demande</option>
              <option value="Congé">Congé</option>
              <option value="Absence">Absence</option>
              <option value="Avance sur Salaire">Avance sur Salaire</option>
              <option value="Autre">Autre</option>
            </select>
            <textarea v-model="hrForm.description" placeholder="Description / Motif" rows="3" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500"></textarea>
            <div class="flex justify-end gap-2 mt-4">
              <button type="button" @click="activeModal = null" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
              <button type="submit" class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg">Soumettre</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="activeModal === 'fuel'" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-xl w-96 shadow-xl">
          <h2 class="text-xl font-bold mb-4 text-gray-900">Demande Carburant</h2>
          <form @submit.prevent="createFuelRequest" class="space-y-3">
            <input v-model="fuelForm.vehicle_plate" placeholder="Plaque Véhicule" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            <select v-model="fuelForm.fuel_type" required class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500">
              <option value="" disabled>Type de carburant</option>
              <option value="Diesel">Diesel</option>
              <option value="Essence">Essence</option>
            </select>
            <input type="number" v-model="fuelForm.amount" placeholder="Montant / Litres (Optionnel)" class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500" />
            <textarea v-model="fuelForm.justification" placeholder="Justification (Optionnel)" rows="2" class="border border-gray-300 px-3 py-2 w-full rounded-lg focus:outline-none focus:border-red-500"></textarea>
            <div class="flex justify-end gap-2 mt-4">
              <button type="button" @click="activeModal = null" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
              <button type="submit" class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg">Soumettre</button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>