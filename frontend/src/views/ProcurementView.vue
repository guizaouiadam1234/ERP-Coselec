<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AppLayout from "@/layouts/AppLayout.vue";
import api from "@/services/api";
import { StockService } from "@/services/stock";
import { useToast } from "@/composables/useToast";
import { getStoredProfile } from "@/services/session";

const toast = useToast();

const purchaseRequests = ref<any[]>([]);
const purchaseOrders = ref<any[]>([]);
const projects = ref<any[]>([]);
const partners = ref<any[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const showRequestModal = ref(false);
const showOrderModal = ref(false);
const isSubmitting = ref(false);

const requestForm = ref({
  project_id: '',
  description: '',
  expected_date: ''
});

const orderForm = ref({
  purchase_request_id: '',
  supplier_id: ''
});

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const [requestsRes, ordersRes, projRes, partRes] = await Promise.all([
      api.get('/procurement/requests'),
      api.get('/procurement/orders'),
      api.get('/projects/'),
      StockService.getPartners()
    ]);
    
    purchaseRequests.value = requestsRes.data;
    purchaseOrders.value = ordersRes.data;
    projects.value = projRes.data;
    partners.value = partRes.data;
  } catch (err: any) {
    console.error("Failed to fetch procurement data", err);
    error.value = "Erreur lors du chargement des données d'achat.";
  } finally {
    loading.value = false;
  }
};

const createPurchaseRequest = async () => {
  if (!requestForm.value.project_id) {
    toast.error("Veuillez sélectionner un projet.");
    return;
  }

  isSubmitting.value = true;
  try {
    // The profile ID is a User ID, not an Employee ID. To avoid FK violations, we send null for now.
    await api.post('/procurement/requests', {
      project_id: Number(requestForm.value.project_id),
      description: requestForm.value.description || undefined,
      expected_date: requestForm.value.expected_date || undefined,
      requester_id: null
    });
    
    toast.success("Demande d'achat créée avec succès !");
    showRequestModal.value = false;
    requestForm.value = { project_id: '', description: '', expected_date: '' };
    await fetchData();
  } catch (err: any) {
    toast.error("Erreur lors de la création de la demande d'achat.");
  } finally {
    isSubmitting.value = false;
  }
};

const createPurchaseOrder = async () => {
  isSubmitting.value = true;
  try {
    await api.post('/procurement/orders', {
      purchase_request_id: orderForm.value.purchase_request_id ? Number(orderForm.value.purchase_request_id) : null,
      supplier_id: orderForm.value.supplier_id ? Number(orderForm.value.supplier_id) : null
    });
    
    toast.success("Bon de commande créé avec succès !");
    showOrderModal.value = false;
    orderForm.value = { purchase_request_id: '', supplier_id: '' };
    await fetchData();
  } catch (err: any) {
    toast.error("Erreur lors de la création du bon de commande.");
  } finally {
    isSubmitting.value = false;
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
          <h1 class="text-3xl font-bold text-gray-900">Module Achats</h1>
          <p class="mt-1 text-gray-500">Gestion des demandes d'achat et bons de commande</p>
        </div>
        <div class="flex gap-4">
          <button @click="showOrderModal = true" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
            Créer un Bon de Commande
          </button>
          <button @click="showRequestModal = true" class="bg-[#d10f2f] hover:bg-[#97091f] text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2">
            <span class="material-symbols-outlined text-sm">add</span>
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

    <!-- Modal Nouvelle Demande d'Achat -->
    <div v-if="showRequestModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-xl w-full max-w-md shadow-xl">
        <h2 class="text-xl font-bold mb-4 text-gray-900">Nouvelle Demande d'Achat</h2>
        <form @submit.prevent="createPurchaseRequest" class="space-y-4">
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Projet</label>
            <select v-model="requestForm.project_id" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500">
              <option value="" disabled>Sélectionner un projet</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.code }} - {{ p.nom }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Date Prévue</label>
            <input type="date" v-model="requestForm.expected_date" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="requestForm.description" rows="3" placeholder="Description de l'achat" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500"></textarea>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showRequestModal = false" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
              Annuler
            </button>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-2 bg-[#d10f2f] hover:bg-[#97091f] text-white rounded-lg font-medium transition-colors disabled:opacity-70 flex items-center justify-center min-w-[120px]">
              <div v-if="isSubmitting" class="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
              <span v-else>Créer</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Nouveau Bon de Commande -->
    <div v-if="showOrderModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-xl w-full max-w-md shadow-xl">
        <h2 class="text-xl font-bold mb-4 text-gray-900">Créer un Bon de Commande</h2>
        <form @submit.prevent="createPurchaseOrder" class="space-y-4">
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Demande d'Achat Liée</label>
            <select v-model="orderForm.purchase_request_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500">
              <option value="">Aucune (Direct)</option>
              <option v-for="req in purchaseRequests" :key="req.id" :value="req.id">DA-{{ req.id }} (Projet #{{ req.project_id }})</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fournisseur</label>
            <select v-model="orderForm.supplier_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500">
              <option value="">Sélectionner un fournisseur</option>
              <option v-for="part in partners" :key="part.id" :value="part.id">{{ part.name }}</option>
            </select>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button type="button" @click="showOrderModal = false" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
              Annuler
            </button>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-2 bg-[#d10f2f] hover:bg-[#97091f] text-white rounded-lg font-medium transition-colors disabled:opacity-70 flex items-center justify-center min-w-[120px]">
              <div v-if="isSubmitting" class="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
              <span v-else>Créer</span>
            </button>
          </div>
        </form>
      </div>
    </div>

  </AppLayout>
</template>
