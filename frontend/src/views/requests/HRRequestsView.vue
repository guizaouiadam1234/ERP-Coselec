<template>
  <AppLayout>
    <div class="min-h-screen bg-gray-50 p-8">
      <header class="mb-10 flex justify-between items-end">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">HR Requests</h1>
          <p class="text-sm text-gray-400 mt-1">Gestion des demandes RH</p>
        </div>
      </header>

      <div class="flex gap-8 w-375 items-start border-2 border-red-100">
        <div
          v-for="status in statuses"
          :key="status.value"
          class="flex-1 flex flex-col rounded-xl border border-transparent p-3 transition"
          :style="{height: columnHeight}"
          :class="dropTargetStatus === status.value ? 'border-red-200 bg-red-100/75' : ''"
          @dragover.prevent="onDragOver(status.value)"
          @dragleave="onDragLeave"
          @drop="onDrop(status.value)"
        >
          <div class="mb-6">
            <h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-2">
              {{ status.label }}
            </h3>
            <div class="w-12 h-0.5 bg-red-600"></div>
          </div>

          <div class="flex flex-col gap-4">
            <div 
              v-for="request in getRequestsByStatus(status.value)" 
              :key="request.id"
              class="bg-white p-5 shadow-sm transition-all duration-300 hover:shadow-md cursor-grab"
              :class="draggingRequestId === request.id ? 'opacity-50' : ''"
              draggable="true"
              @dragstart="onDragStart(request.id)"
              @dragend="onDragEnd"
            >
              <span class="block text-[10px] font-mono text-red-500 mb-2">HR-{{ request.id }}</span>
              <h4 class="text-sm font-semibold text-gray-900 leading-tight mb-3">
                Demande: {{ request.request_type }}
              </h4>
              <div class="flex justify-between items-center">
                <span class="text-[10px] text-gray-400 uppercase font-medium">Emp: {{ request.employee_id }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';
import AppLayout from '@/layouts/AppLayout.vue';

const requests = ref([]);
const draggingRequestId = ref(null);
const dropTargetStatus = ref(null);
const isUpdatingStatus = ref(false);

const statuses = [
  { label: 'En attente', value: 'Pending' },
  { label: 'Approuvé', value: 'Approved' },
  { label: 'Refusé', value: 'Rejected' }
];

const getRequestsByStatus = (statusValue) => {
  return requests.value.filter(t => t.status === statusValue);
};

const loadRequests = async () => {
  try {
    const response = await api.get('/hr-requests/');
    requests.value = response.data;
  } catch (err) {
    console.error("Erreur", err);
  }
};

const onDragStart = (requestId) => {
  draggingRequestId.value = requestId;
};

const onDragEnd = () => {
  draggingRequestId.value = null;
  dropTargetStatus.value = null;
};

const onDragOver = (statusValue) => {
  dropTargetStatus.value = statusValue;
};

const onDragLeave = () => {
  dropTargetStatus.value = null;
};

const onDrop = async (targetStatus) => {
  if (draggingRequestId.value === null || isUpdatingStatus.value) return;

  const request = requests.value.find((item) => item.id === draggingRequestId.value);
  if (!request || request.status === targetStatus) {
    onDragEnd();
    return;
  }

  let rejection_comment = null;
  if (['Resolved', 'Rejected', 'Approved'].includes(targetStatus)) {
    rejection_comment = window.prompt("Ajouter un commentaire (optionnel) :");
  }

  isUpdatingStatus.value = true;

  try {
    const response = await api.put(`/hr-requests/${request.id}`, { 
      status: targetStatus,
      rejection_comment: rejection_comment || undefined
    });
    const updatedRequest = response.data;
    requests.value = requests.value.map((item) =>
      item.id === updatedRequest.id ? updatedRequest : item
    );
  } catch (error) {
    console.error('Erreur', error);
    alert("Impossible de changer le statut.");
  } finally {
    isUpdatingStatus.value = false;
    onDragEnd();
  }
};

const maxRequestsInColumn = computed(() => {
  const max = Math.max(
    ...statuses.map(status => getRequestsByStatus(status.value).length),
    0
  );
  return max;
});

const columnHeight = computed(() => {
  const requestHeight = 120;
  const padding = 100;
  return `${maxRequestsInColumn.value * requestHeight + padding}px`;
});

onMounted(async () => {
  await loadRequests();
});
</script>
