<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AppLayout from "@/layouts/AppLayout.vue";
import api from "@/services/api";
import { StockService } from '@/services/stock';
import { useToast } from '@/composables/useToast';
import { getStoredProfile } from '@/services/session';

const toast = useToast();

const reservations = ref<any[]>([]);
const projects = ref<any[]>([]);
const products = ref<any[]>([]);

const loading = ref(true);
const error = ref<string | null>(null);

const showModal = ref(false);
const isSubmitting = ref(false);

const form = ref({
  project_id: '',
  product_id: '',
  quantity: 1
});

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const [resData, projData, prodData] = await Promise.all([
      api.get('/stock-reservations/'),
      api.get('/projects/'),
      StockService.getProducts()
    ]);
    
    reservations.value = resData.data;
    projects.value = projData.data;
    products.value = prodData.data;
  } catch (err: any) {
    error.value = "Erreur lors du chargement des données.";
  } finally {
    loading.value = false;
  }
};

const createReservation = async () => {
  if (!form.value.project_id || !form.value.product_id || form.value.quantity < 1) {
    toast.error("Veuillez remplir tous les champs correctement.");
    return;
  }

  isSubmitting.value = true;
  try {
    // The profile ID is a User ID, not an Employee ID. To avoid FK violations, we send null for now.
    await api.post('/stock-reservations/', {
      project_id: Number(form.value.project_id),
      product_id: Number(form.value.product_id),
      quantity: form.value.quantity,
      reserved_by_id: null
    });
    
    toast.success("Réservation créée avec succès !");
    showModal.value = false;
    form.value = { project_id: '', product_id: '', quantity: 1 };
    await fetchData();
  } catch (err: any) {
    const msg = err.response?.data?.detail || "Erreur lors de la création de la réservation.";
    toast.error(msg);
  } finally {
    isSubmitting.value = false;
  }
};

const consumeReservation = async (reservationId: number) => {
  try {
    await api.post(`/stock-reservations/${reservationId}/consume`);
    toast.success("Réservation consommée !");
    await fetchData();
  } catch (err: any) {
    const msg = err.response?.data?.detail || "Erreur lors de la consommation.";
    toast.error(msg);
  }
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <AppLayout>
    <div class="max-w-7xl mx-auto space-y-8 w-full">
      
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Réservations de Stock</h1>
          <p class="mt-1 text-gray-500">Gérer les réservations d'articles pour les projets</p>
        </div>
        <div class="flex gap-4">
          <button @click="showModal = true" class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2">
            <span class="material-symbols-outlined text-sm">add</span>
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
                <td class="px-6 py-4 text-sm">
                  <button 
                    v-if="res.status !== 'Consumed'"
                    @click="consumeReservation(res.id)"
                    class="text-blue-600 hover:underline font-medium"
                  >
                    Consommer
                  </button>
                  <span v-else class="text-gray-400">Consommée</span>
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

    <!-- Nouvelle Réservation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-xl w-full max-w-md shadow-xl">
        <h2 class="text-xl font-bold mb-4 text-gray-900">Nouvelle Réservation</h2>
        <form @submit.prevent="createReservation" class="space-y-4">
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Projet</label>
            <select v-model="form.project_id" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500">
              <option value="" disabled>Sélectionner un projet</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.code }} - {{ p.nom }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Produit</label>
            <select v-model="form.product_id" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500">
              <option value="" disabled>Sélectionner un produit</option>
              <option v-for="prod in products" :key="prod.id" :value="prod.id">{{ prod.designation || prod.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Quantité</label>
            <input type="number" v-model.number="form.quantity" min="1" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500" />
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showModal = false" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
              Annuler
            </button>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-2 bg-[#d10f2f] hover:bg-[#97091f] text-white rounded-lg font-medium transition-colors disabled:opacity-70 flex items-center justify-center min-w-[120px]">
              <div v-if="isSubmitting" class="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
              <span v-else>Réserver</span>
            </button>
          </div>
        </form>
      </div>
    </div>

  </AppLayout>
</template>
