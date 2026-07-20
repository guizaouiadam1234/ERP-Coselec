<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";
import api from "@/services/api";

const route = useRoute();
const projectId = route.params.id || 'N/A';

const budgets = ref<any[]>([]);
const expenses = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  if (projectId === 'N/A') {
    error.value = "ID du projet manquant.";
    loading.value = false;
    return;
  }

  try {
    const [budgetsRes, expensesRes] = await Promise.all([
      api.get(`/projects/${projectId}/budgets`),
      api.get(`/projects/${projectId}/budgets/expenses`)
    ]);
    
    budgets.value = budgetsRes.data;
    expenses.value = expensesRes.data;
  } catch (err: any) {
    console.error("Failed to fetch project budget data", err);
    error.value = "Erreur lors du chargement des budgets.";
  } finally {
    loading.value = false;
  }
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
              <h1 class="text-3xl font-bold text-gray-900">Suivi du Budget Projet #{{ projectId }}</h1>
              <p class="mt-1 text-gray-500">Gestion des budgets alloués et des dépenses</p>
            </div>
            <div class="flex gap-4">
              <button class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                Nouvelle Dépense
              </button>
              <button class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg transition-colors">
                Ajouter un Budget
              </button>
            </div>
          </div>

          <div v-if="loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#d10f2f]"></div>
          </div>

          <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg">
            {{ error }}
          </div>

          <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Budgets Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div class="p-6 border-b border-gray-100">
                <h2 class="text-xl font-bold text-gray-900">Lignes Budgétaires</h2>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left">
                  <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <tr>
                      <th class="px-6 py-4 font-medium">Catégorie</th>
                      <th class="px-6 py-4 font-medium">Alloué</th>
                      <th class="px-6 py-4 font-medium">Consommé</th>
                      <th class="px-6 py-4 font-medium">Restant</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="b in budgets" :key="b.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ b.category }}</td>
                      <td class="px-6 py-4 text-sm text-gray-500">{{ b.allocated_amount }} {{ b.currency }}</td>
                      <td class="px-6 py-4 text-sm text-red-600">{{ b.consumed }} {{ b.currency }}</td>
                      <td class="px-6 py-4 text-sm font-bold text-green-600">{{ b.allocated_amount - b.consumed }} {{ b.currency }}</td>
                    </tr>
                    <tr v-if="budgets.length === 0">
                      <td colspan="4" class="px-6 py-8 text-center text-gray-500">Aucun budget défini.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Expenses Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div class="p-6 border-b border-gray-100">
                <h2 class="text-xl font-bold text-gray-900">Dernières Dépenses</h2>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left">
                  <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <tr>
                      <th class="px-6 py-4 font-medium">Date</th>
                      <th class="px-6 py-4 font-medium">Description</th>
                      <th class="px-6 py-4 font-medium">Montant</th>
                      <th class="px-6 py-4 font-medium">Statut</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="e in expenses" :key="e.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 text-sm text-gray-500">{{ e.date_incurred }}</td>
                      <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ e.description || '-' }}</td>
                      <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ e.amount }} XOF</td>
                      <td class="px-6 py-4">
                        <span :class="{'bg-green-100 text-green-800': e.status === 'Approved', 'bg-yellow-100 text-yellow-800': e.status === 'Pending', 'bg-red-100 text-red-800': e.status === 'Rejected'}" class="px-2 py-1 text-xs font-semibold rounded-full">
                          {{ e.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="expenses.length === 0">
                      <td colspan="4" class="px-6 py-8 text-center text-gray-500">Aucune dépense enregistrée.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  </div>
</template>
