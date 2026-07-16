<template>
  <div class="flex h-screen overflow-hidden">
    <Sidebar />
    <div class="flex-1 flex flex-col relative">
      <Navbar />
      <main class="flex-1 p-6 bg-gradient-to-br from-red-50 via-white to-red-100/50 overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold mb-4 text-[#b30c27] flex items-center gap-2">
            <span class="material-symbols-outlined">local_gas_station</span>
            <span>Demandes de Carburant (DMCAR)</span>
          </h1>
          <button 
            @click="showCreateModal = true"
            class="bg-[#d10f2f] text-white px-4 py-2 rounded-xl hover:bg-[#97091f] shadow-[0_10px_30px_rgba(209,15,47,0.28)] transition flex items-center gap-2 mb-6"
          >
            <span class="material-symbols-outlined">add</span>
            <span>Nouvelle Demande</span>
          </button>
        </div>

        <!-- Tableau des demandes -->
        <div class="bg-white rounded-2xl shadow-[0_15px_40px_rgba(127,7,28,0.10)] border border-red-100 overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-gradient-to-r from-red-100/90 to-red-50 text-left">
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">Date</th>
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">Employé / Véhicule</th>
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">Quantité</th>
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">Statut</th>
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">PDF</th>
                <th class="px-6 py-4 text-sm font-semibold text-[#7f071c]">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in requests" :key="req.id" class="border-t border-red-100/80 hover:bg-red-50/70 transition">
                <td class="px-6 py-4 text-gray-600 font-medium whitespace-nowrap">{{ req.request_date }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ req.employee_name || 'N/A' }}</div>
                  <div class="text-xs text-gray-500">{{ req.vehicule_matricule }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ req.quantite_carburant }} L</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-3 py-1 rounded-full text-xs font-medium uppercase bg-amber-100 text-amber-700">
                    {{ req.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <a v-if="req.pdf_url" :href="getPdfUrl(req.pdf_url)" target="_blank" class="text-indigo-600 hover:text-indigo-900 flex items-center gap-1 font-semibold">
                    <span class="material-symbols-outlined text-lg">picture_as_pdf</span>
                    Télécharger PDF
                  </a>
                  <span v-else class="text-gray-400 italic">Non généré</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button 
                    v-if="req.status === 'PENDING_FINANCE'" 
                    @click="validateFinance(req.id)"
                    class="text-emerald-600 hover:text-emerald-900"
                  >
                    Valider Finance
                  </button>
                  <button 
                    @click="deleteRequest(req.id)"
                    class="ml-3 text-red-600 hover:text-red-900"
                    title="Supprimer la demande"
                  >
                    <span class="material-symbols-outlined text-lg align-middle">delete</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>

    <!-- Modal Nouvelle Demande -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
        <div class="px-6 py-4 bg-[#b30c27] text-white flex justify-between items-center">
          <h2 class="text-xl font-bold flex items-center gap-2">
            <span class="material-symbols-outlined">description</span>
            Nouvelle Demande de Carburant
          </h2>
          <button @click="showCreateModal = false" class="hover:bg-[#d10f2f] p-1 rounded-full transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <form @submit.prevent="submitRequest" class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Employé</label>
              <select 
                v-model="form.employee_id" 
                required
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
              >
                <option value="" disabled>Sélectionner un employé</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.first_name }} {{ emp.last_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input 
                type="date" 
                v-model="form.request_date" 
                required
                class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">N° Affaire (Optionnel)</label>
              <input type="text" v-model="form.affaire_no" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">N° Dossier (Optionnel)</label>
              <input type="text" v-model="form.dossier_no" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Objet du Déplacement</label>
              <input type="text" v-model="form.objet_deplacement" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Matricule Véhicule</label>
              <input type="text" v-model="form.vehicule_matricule" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Destination</label>
              <input type="text" v-model="form.destination" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Relevé Kilométrique</label>
              <input type="number" v-model="form.releve_kilometrique" required min="1" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de jours</label>
              <input type="number" v-model="form.nombre_jours" required min="1" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Quantité de carburant (Litres)</label>
              <input type="number" step="0.01" v-model="form.quantite_carburant" required min="0.01" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
            </div>
          </div>
          <div class="mt-8 flex justify-end gap-3 pt-4 border-t">
            <button type="button" @click="showCreateModal = false" class="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-xl transition">
              Annuler
            </button>
            <button type="submit" class="px-6 py-2 bg-[#d10f2f] text-white hover:bg-[#97091f] rounded-xl shadow-lg transition">
              Créer la demande
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import Navbar from '@/components/Navbar.vue';
import { api } from '@/services/api';
import { employeeService } from '@/services/employees';

const requests = ref<any[]>([]);
const employees = ref<any[]>([]);
const showCreateModal = ref(false);

const getPdfUrl = (url: string) => {
  return `http://${window.location.hostname}:8000/${url}`;
};

const form = ref({
  employee_id: '',
  request_date: new Date().toISOString().split('T')[0],
  vehicule_matricule: '',
  objet_deplacement: '',
  destination: '',
  releve_kilometrique: 0,
  nombre_jours: 1,
  quantite_carburant: 0,
});

async function fetchRequests() {
  try {
    const res = await api.get('/fuel-requests/');
    requests.value = res.data;
  } catch (e) {
    console.error("Error fetching requests", e);
  }
}

async function fetchEmployees() {
  try {
    const res = await employeeService.getAllEmployees();
    employees.value = res.data;
  } catch (e) {
    console.error("Error fetching employees", e);
  }
}

async function submitRequest() {
  try {
    await api.post('/fuel-requests/', form.value);
    showCreateModal.value = false;
    // Reset form
    form.value.employee_id = '';
    form.value.vehicule_matricule = '';
    form.value.objet_deplacement = '';
    form.value.destination = '';
    form.value.releve_kilometrique = 0;
    form.value.quantite_carburant = 0;
    
    await fetchRequests();
  } catch (e) {
    console.error("Error creating request", e);
    alert("Erreur lors de la création de la demande");
  }
}

async function validateFinance(id: number) {
  try {
    await api.post(`/fuel-requests/${id}/validate/finance/`, {
      action: 'APPROVE'
    });
    await fetchRequests();
    alert("Demande validée ! Le PDF a été généré dans MinIO.");
  } catch (e) {
    console.error("Error validating", e);
    alert("Erreur lors de la validation. Vérifiez vos permissions.");
  }
}

async function deleteRequest(id: number) {
  if (!confirm("Voulez-vous vraiment supprimer cette demande ?")) return;
  try {
    await api.delete(`/fuel-requests/${id}`);
    await fetchRequests();
  } catch (e) {
    console.error("Error deleting request", e);
    alert("Erreur lors de la suppression. Vérifiez vos permissions.");
  }
}

onMounted(() => {
  fetchRequests();
  fetchEmployees();
});
</script>
