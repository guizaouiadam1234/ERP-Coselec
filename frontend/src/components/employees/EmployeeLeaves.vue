<script setup lang="ts">
import axios from 'axios';
import { ref, watch, computed } from 'vue';
import { leaveService, type LeaveRequest, type LeaveRequestCreate } from '@/services/leaves';

const props = defineProps<{
  employeeId: number;
}>();

const leaves = ref<LeaveRequest[]>([]);
const loading = ref(true);
const errorMessage = ref('');
const showForm = ref(false);

const sortColumn = ref('');
const sortOrder = ref<'asc' | 'desc'>('asc');

const sortBy = (column: string) => {
  if (sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortOrder.value = 'asc';
  }
};

const sortedLeaves = computed(() => {
  if (!sortColumn.value) return leaves.value;
  return [...leaves.value].sort((a, b) => {
    let valA = (a as any)[sortColumn.value];
    let valB = (b as any)[sortColumn.value];

    if (valA === null || valA === undefined) valA = '';
    if (valB === null || valB === undefined) valB = '';

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1;
    return 0;
  });
});

const getErrorMessage = (error: unknown, fallback: string) => {
  if (axios.isAxiosError(error) && error.response?.status === 403) {
    return "Acces refuse sur les conges. Redemarre le backend ou verifie les permissions du role.";
  }

  return fallback;
};

const form = ref<Omit<LeaveRequestCreate, 'employee_id'>>({
  leave_type: 'Congé payé',
  start_date: '',
  end_date: '',
  reason: ''
});

const loadLeaves = async () => {
  if (!props.employeeId) return;
  try {
    loading.value = true;
    errorMessage.value = '';
    leaves.value = await leaveService.getByEmployee(props.employeeId);
  } catch (error) {
    errorMessage.value = getErrorMessage(error, "Erreur lors du chargement des conges.");
  } finally {
    loading.value = false;
  }
};

watch(() => props.employeeId, () => {
  loadLeaves();
}, { immediate: true });

const handleSubmit = async () => {
  try {
    errorMessage.value = '';
    const payload: LeaveRequestCreate = {
      ...form.value,
      employee_id: props.employeeId,
      reason: form.value.reason || null
    };
    await leaveService.create(payload);
    showForm.value = false;
    form.value = { leave_type: 'Congé payé', start_date: '', end_date: '', reason: '' };
    await loadLeaves();
  } catch (error) {
    errorMessage.value = getErrorMessage(error, "Impossible d'enregistrer la demande.");
  }
};

const handleDelete = async (id: number) => {
  if (confirm('Supprimer cette demande de congé ?')) {
    try {
      errorMessage.value = '';
      await leaveService.delete(id);
      await loadLeaves();
    } catch (error) {
      errorMessage.value = getErrorMessage(error, "Impossible de supprimer la demande.");
    }
  }
};

const getLeaveTypeColor = (type: string) => {
  switch (type) {
    case 'Maladie': return 'bg-red-50 text-red-700 border-red-200';
    case 'Sans solde': return 'bg-stone-100 text-stone-700 border-stone-200';
    case 'Maternité/Paternité': return 'bg-rose-50 text-rose-700 border-rose-200';
    default: return 'bg-white text-[#b3232b] border-red-200';
  }
};
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-4 rounded-2xl border border-red-100 bg-[linear-gradient(180deg,_#fff_0%,_#fff7f8_100%)] px-4 py-4 shadow-sm">
      <div>
        <h3 class="text-lg font-black tracking-tight text-gray-950">Conges & Absences</h3>
        <p class="mt-1 text-xs text-gray-500">Saisie RH directe avec application immediate dans le planning departements.</p>
      </div>
      <button 
        @click="showForm = !showForm"
        class="inline-flex items-center gap-2 rounded-xl bg-[#d10f2f] px-3.5 py-2 text-xs font-semibold text-white shadow-lg shadow-red-100 transition hover:bg-[#97091f]"
      >
        <span class="material-symbols-outlined text-sm">event_available</span>
        {{ showForm ? 'Annuler' : 'Nouveau conge' }}
      </button>
    </div>

    <div v-if="errorMessage" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ errorMessage }}
    </div>

    <div v-if="showForm" class="max-w-2xl rounded-2xl border border-red-100 bg-white p-5 shadow-[0_14px_40px_rgba(127,7,28,0.08)]">
      <form @submit.prevent="handleSubmit" class="space-y-3 text-sm">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-500">Type d'absence</label>
          <select v-model="form.leave_type" class="w-full rounded-xl border border-red-100 bg-[#fffafb] p-3 text-gray-800 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-100">
            <option value="Congé payé">Congé payé</option>
            <option value="Maladie">Maladie</option>
            <option value="Sans solde">Sans solde</option>
            <option value="Maternité/Paternité">Maternité / Paternité</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-500">Date de debut</label>
            <input type="date" v-model="form.start_date" required class="w-full rounded-xl border border-red-100 bg-[#fffafb] p-3 text-gray-800 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-100" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-500">Date de fin</label>
            <input type="date" v-model="form.end_date" required class="w-full rounded-xl border border-red-100 bg-[#fffafb] p-3 text-gray-800 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-100" />
          </div>
        </div>
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-gray-500">Motif</label>
          <input type="text" v-model="form.reason" placeholder="Ex: Raison familiale..." class="w-full rounded-xl border border-red-100 bg-[#fffafb] p-3 text-gray-800 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-100" />
        </div>
        
        <button type="submit" class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#d10f2f] py-3 font-semibold text-white shadow-lg shadow-red-100 transition hover:bg-[#97091f]">
          <span class="material-symbols-outlined text-sm">send</span>
          Soumettre le conge
        </button>
      </form>
    </div>

    <div v-if="loading" class="rounded-2xl border border-red-100 bg-white px-4 py-10 text-center text-sm text-gray-400 shadow-sm">Chargement des conges...</div>

    <div v-else class="overflow-hidden rounded-2xl border border-red-100 bg-white shadow-[0_14px_40px_rgba(127,7,28,0.08)]">
      <table class="min-w-full divide-y divide-red-100 text-left text-xs">
        <thead class="bg-[linear-gradient(180deg,_#fffafa_0%,_#fff2f4_100%)] text-gray-500 font-semibold uppercase tracking-wide">
          <tr>
            <th @click="sortBy('leave_type')" class="px-4 py-3 cursor-pointer hover:bg-gray-100 transition">
              <div class="flex items-center gap-1">Type <span v-if="sortColumn === 'leave_type'" class="material-symbols-outlined text-[10px]">{{ sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward' }}</span></div>
            </th>
            <th @click="sortBy('start_date')" class="px-4 py-3 cursor-pointer hover:bg-gray-100 transition">
              <div class="flex items-center gap-1">Periode <span v-if="sortColumn === 'start_date'" class="material-symbols-outlined text-[10px]">{{ sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward' }}</span></div>
            </th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-red-50 text-gray-600">
          <tr v-for="leave in sortedLeaves" :key="leave.id" class="transition-colors hover:bg-red-50/40">
            <td class="px-4 py-4 font-semibold text-gray-900">
              <span :class="getLeaveTypeColor(leave.leave_type)" class="inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide">
                {{ leave.leave_type }}
              </span>
              <p v-if="leave.reason" class="mt-2 max-w-[220px] truncate text-[11px] font-normal text-gray-500" :title="leave.reason">{{ leave.reason }}</p>
            </td>
            <td class="px-4 py-4 text-gray-500">
              Du {{ leave.start_date }}<br/>Au {{ leave.end_date }}
            </td>
            <td class="px-4 py-4 text-right">
              <div class="flex justify-end items-center gap-2">
                <button v-if="leave.pdf_url" @click="leaveService.downloadCertificate(leave.id)" class="rounded-lg p-1.5 text-blue-600 transition hover:bg-blue-50" title="Imprimer l'attestation">
                  <span class="material-symbols-outlined text-sm">print</span>
                </button>
                <button @click="handleDelete(leave.id)" class="rounded-lg p-1.5 text-red-600 transition hover:bg-red-50" title="Supprimer">
                  <span class="material-symbols-outlined text-sm">delete</span>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="leaves.length === 0">
            <td colspan="3" class="px-4 py-10 text-center text-sm text-gray-400">Aucun conge enregistre.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>