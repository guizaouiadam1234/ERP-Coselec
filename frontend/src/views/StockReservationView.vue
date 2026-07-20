<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";
import api from "@/services/api";

const reservations = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    const res = await api.get('/stock-reservations/');
    reservations.value = res.data;
  } catch (err: any) {
    console.error("Failed to fetch stock reservations", err);
    error.value = "Erreur lors du chargement des réservations de stock.";
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
              <h1 class="text-3xl font-bold text-gray-900">Réservations de Stock</h1>
              <p class="mt-1 text-gray-500">Gérer les réservations d'articles pour les projets</p>
            </div>
            <div class="flex gap-4">
              <button class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg transition-colors">
                Nouvelle Réservation
              </button>
            </div>
          </div>

          <div v-if="loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#d10f2f]"></div>
          </div>

          <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg">
            {{ error }}
          </div>

          <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="p-6 border-b border-gray-100">
              <h2 class="text-xl font-bold text-gray-900">Liste des Réservations</h2>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left">
                <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                  <tr>
                    <th class="px-6 py-4 font-medium">ID Réservation</th>
                    <th class="px-6 py-4 font-medium">Projet</th>
                    <th class="px-6 py-4 font-medium">Produit</th>
                    <th class="px-6 py-4 font-medium">Quantité</th>
                    <th class="px-6 py-4 font-medium">Date</th>
                    <th class="px-6 py-4 font-medium">Statut</th>
                    <th class="px-6 py-4 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="res in reservations" :key="res.id" class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm font-bold text-gray-900">RES-{{ res.id }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">#{{ res.project_id }}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ res.product_name || `Produit #${res.product_id}` }}</td>
                    <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ res.quantity }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500">{{ new Date(res.created_at).toLocaleDateString() }}</td>
                    <td class="px-6 py-4">
                      <span :class="{'bg-green-100 text-green-800': res.status === 'Approved' || res.status === 'Consumed', 'bg-yellow-100 text-yellow-800': res.status === 'Pending'}" class="px-2 py-1 text-xs font-semibold rounded-full">
                        {{ res.status }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-blue-600 cursor-pointer hover:underline">
                      Consommer
                    </td>
                  </tr>
                  <tr v-if="reservations.length === 0">
                    <td colspan="7" class="px-6 py-8 text-center text-gray-500">Aucune réservation de stock.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
        </div>
      </main>
    </div>
  </div>
</template>
