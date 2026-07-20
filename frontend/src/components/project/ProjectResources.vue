<template>
  <div class="flex flex-col gap-6">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900">Ressources Matérielles (Réservations de Stock)</h2>
        <router-link to="/stock-reservations" class="text-sm text-[#d10f2f] hover:underline font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">open_in_new</span>
          Gérer les réservations
        </router-link>
      </div>
      
      <div class="p-6" v-if="loading">
        <div class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#d10f2f]"></div>
        </div>
      </div>
      
      <div class="p-6" v-else-if="error">
        <div class="bg-red-50 text-red-600 p-4 rounded-lg text-sm">{{ error }}</div>
      </div>

      <div class="overflow-x-auto" v-else>
        <table class="w-full text-left">
          <thead class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
            <tr>
              <th class="px-6 py-4 font-medium">ID Réservation</th>
              <th class="px-6 py-4 font-medium">Produit</th>
              <th class="px-6 py-4 font-medium">Quantité</th>
              <th class="px-6 py-4 font-medium">Date de Réservation</th>
              <th class="px-6 py-4 font-medium">Statut</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="res in reservations" :key="res.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 text-sm font-bold text-gray-900">RES-{{ res.id }}</td>
              <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ res.product_name || `Produit #${res.product_id}` }}</td>
              <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ res.quantity }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ new Date(res.created_at).toLocaleDateString() }}</td>
              <td class="px-6 py-4">
                <span :class="{'bg-green-100 text-green-800': res.status === 'Approved' || res.status === 'Consumed', 'bg-yellow-100 text-yellow-800': res.status === 'Pending'}" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ res.status }}
                </span>
              </td>
            </tr>
            <tr v-if="reservations.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-gray-500">Aucune ressource matérielle réservée pour ce projet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import api from '@/services/api';

const props = defineProps<{
  projectId: number | string | null
}>();

const reservations = ref<any[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const fetchResources = async () => {
  if (!props.projectId) {
    reservations.value = [];
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const res = await api.get('/stock-reservations/');
    // Filter to show only reservations for the active project
    reservations.value = res.data.filter((r: any) => String(r.project_id) === String(props.projectId));
  } catch (err: any) {
    error.value = "Impossible de charger les ressources matérielles.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

watch(() => props.projectId, () => {
  fetchResources();
}, { immediate: true });

onMounted(() => {
  if (!loading.value && reservations.value.length === 0) {
    fetchResources();
  }
});
</script>
