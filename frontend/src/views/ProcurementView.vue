<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";
import api from "@/services/api";

const purchaseRequests = ref<any[]>([]);
const purchaseOrders = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    const [requestsRes, ordersRes] = await Promise.all([
      api.get('/procurement/requests'),
      api.get('/procurement/orders')
    ]);
    
    purchaseRequests.value = requestsRes.data;
    purchaseOrders.value = ordersRes.data;
  } catch (err: any) {
    console.error("Failed to fetch procurement data", err);
    error.value = "Erreur lors du chargement des données d'achat.";
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
              <h1 class="text-3xl font-bold text-gray-900">Module Achats</h1>
              <p class="mt-1 text-gray-500">Gestion des demandes d'achat et bons de commande</p>
            </div>
            <div class="flex gap-4">
              <button class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                Créer un Bon de Commande
              </button>
              <button class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg transition-colors">
                Nouvelle Demande
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
            <!-- Purchase Requests -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div class="p-6 border-b border-gray-100">
                <h2 class="text-xl font-bold text-gray-900">Demandes d'Achats</h2>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left">
                  <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <tr>
                      <th class="px-6 py-4 font-medium">Projet</th>
                      <th class="px-6 py-4 font-medium">Description</th>
                      <th class="px-6 py-4 font-medium">Date Prévue</th>
                      <th class="px-6 py-4 font-medium">Statut</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="req in purchaseRequests" :key="req.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 text-sm font-medium text-gray-900">#{{ req.project_id }}</td>
                      <td class="px-6 py-4 text-sm text-gray-500">{{ req.description || '-' }}</td>
                      <td class="px-6 py-4 text-sm text-gray-500">{{ req.expected_date || '-' }}</td>
                      <td class="px-6 py-4">
                        <span :class="{'bg-green-100 text-green-800': req.status === 'Approved', 'bg-yellow-100 text-yellow-800': req.status === 'Pending'}" class="px-2 py-1 text-xs font-semibold rounded-full">
                          {{ req.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="purchaseRequests.length === 0">
                      <td colspan="4" class="px-6 py-8 text-center text-gray-500">Aucune demande d'achat.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Purchase Orders -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div class="p-6 border-b border-gray-100">
                <h2 class="text-xl font-bold text-gray-900">Bons de Commande</h2>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left">
                  <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <tr>
                      <th class="px-6 py-4 font-medium">ID BC</th>
                      <th class="px-6 py-4 font-medium">Demande Liée</th>
                      <th class="px-6 py-4 font-medium">Montant Total</th>
                      <th class="px-6 py-4 font-medium">Statut</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="order in purchaseOrders" :key="order.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 text-sm font-bold text-gray-900">BC-{{ order.id }}</td>
                      <td class="px-6 py-4 text-sm text-gray-500">DA-{{ order.purchase_request_id || '-' }}</td>
                      <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ order.total_amount }} XOF</td>
                      <td class="px-6 py-4">
                        <span :class="{'bg-blue-100 text-blue-800': order.status === 'Issued', 'bg-gray-100 text-gray-800': order.status === 'Draft'}" class="px-2 py-1 text-xs font-semibold rounded-full">
                          {{ order.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="purchaseOrders.length === 0">
                      <td colspan="4" class="px-6 py-8 text-center text-gray-500">Aucun bon de commande.</td>
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
