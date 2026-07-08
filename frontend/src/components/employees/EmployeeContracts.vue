<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { contractService, type Contract, type ContractCreate } from '@/services/contracts';

const props = defineProps<{
  employeeId: number;
}>();

const contracts = ref<Contract[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const showForm = ref(false);

// Modèle pour le formulaire d'ajout
const form = ref<Omit<ContractCreate, 'employee_id'>>({
  contract_type: 'CDI',
  start_date: '',
  end_date: null,
  is_active: true
});

const loadEmployeeContracts = async () => {
  try {
    loading.value = true;
    const allContracts = await contractService.getAll();
    // Filtrage pour n'avoir que les contrats de l'employé en cours
    contracts.value = allContracts.filter(c => c.employee_id === props.employeeId);
  } catch (error) {
    errorMessage.value = "Erreur lors du chargement des contrats.";
  } finally {
    loading.value = false;
  }
};

// Recharger si l'ID de l'employé change sans recharger le composant
watch(() => props.employeeId, () => {
  loadEmployeeContracts();
}, { immediate: true });

const handleSubmit = async () => {
  try {
    const payload: ContractCreate = {
      ...form.value,
      employee_id: props.employeeId,
      end_date: form.value.end_date || null
    };
    await contractService.create(payload);
    showForm.value = false;
    // Réinitialisation du formulaire
    form.value = { contract_type: 'CDI', start_date: '', end_date: null, is_active: true };
    await loadEmployeeContracts();
  } catch (error) {
    errorMessage.value = "Impossible d'enregistrer le contrat.";
  }
};

const handleDelete = async (id: number) => {
  if (confirm('Supprimer ce contrat ?')) {
    try {
      await contractService.delete(id);
      await loadEmployeeContracts();
    } catch (error) {
      console.error(error);
    }
  }
};
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900">Historique des Contrats</h3>
      <button 
        @click="showForm = !showForm"
        class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-2 px-3 rounded-lg transition-colors"
      >
        {{ showForm ? 'Annuler' : 'Nouveau Contrat' }}
      </button>
    </div>

    <div v-if="showForm" class="bg-gray-50 p-4 rounded-xl border border-gray-200 shadow-inner max-w-md">
      <form @submit.prevent="handleSubmit" class="space-y-3 text-sm">
        <div>
          <label class="block text-xs font-medium text-gray-500 uppercase mb-1">Type de contrat</label>
          <select v-model="form.contract_type" class="w-full border border-gray-300 rounded-lg p-2 bg-white">
            <option value="CDI">CDI</option>
            <option value="CDD">CDD</option>
            <option value="Stagiaire">Stagiaire</option>
            <option value="Alternant">Alternant</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 uppercase mb-1">Date de début</label>
          <input type="date" v-model="form.start_date" required class="w-full border border-gray-300 rounded-lg p-2 bg-white" />
        </div>
        <div v-if="form.contract_type !== 'CDI'">
          <label class="block text-xs font-medium text-gray-500 uppercase mb-1">Date de fin</label>
          <input type="date" v-model="form.end_date" class="w-full border border-gray-300 rounded-lg p-2 bg-white" />
        </div>
        <div class="flex items-center space-x-2 py-1">
          <input type="checkbox" v-model="form.is_active" id="comp_is_active" class="rounded text-blue-600" />
          <label for="comp_is_active" class="text-xs text-gray-600">Contrat actif</label>
        </div>
        <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded-lg transition-colors">
          Enregistrer le contrat
        </button>
      </form>
    </div>

    <div v-if="loading" class="text-center py-4 text-sm text-gray-400">Chargement des contrats...</div>

    <div v-else class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-xs">
      <table class="min-w-full divide-y divide-gray-200 text-left text-xs">
        <thead class="bg-gray-50 text-gray-500 font-medium uppercase">
          <tr>
            <th class="px-4 py-2">Type</th>
            <th class="px-4 py-2">Début</th>
            <th class="px-4 py-2">Fin</th>
            <th class="px-4 py-2">Statut</th>
            <th class="px-4 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-gray-600">
          <tr v-for="contract in contracts" :key="contract.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-semibold text-gray-900">{{ contract.contract_type }}</td>
            <td class="px-4 py-3">{{ contract.start_date }}</td>
            <td class="px-4 py-3">{{ contract.end_date || 'Indéterminée' }}</td>
            <td class="px-4 py-3">
              <span :class="contract.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-0.5 rounded-full text-[10px] font-medium">
                {{ contract.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button @click="handleDelete(contract.id)" class="text-red-600 hover:text-red-900 font-medium">Supprimer</button>
            </td>
          </tr>
          <tr v-if="contracts.length === 0">
            <td colspan="5" class="px-4 py-6 text-center text-gray-400">Aucun contrat enregistré pour cet employé.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>