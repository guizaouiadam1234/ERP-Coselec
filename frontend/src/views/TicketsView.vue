<template>
  <AppLayout>
    <div class="min-h-screen bg-gray-50 p-8">
      <header class="mb-10 flex justify-between items-end">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Helpdesk</h1>
          <p class="text-sm text-gray-400 mt-1">Gestion des demandes internes</p>
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
              v-for="ticket in getTicketsByStatus(status.value)" 
              :key="ticket.id"
              class="bg-white p-5 shadow-sm transition-all duration-300 hover:shadow-md cursor-grab"
              :class="draggingTicketId === ticket.id ? 'opacity-50' : ''"
              draggable="true"
              @dragstart="onDragStart(ticket.id)"
              @dragend="onDragEnd"
            >
              <span class="block text-[10px] font-mono text-red-500 mb-2">TICKET-{{ ticket.id }}</span>
              <h4 class="text-sm font-semibold text-gray-900 leading-tight mb-3">
                {{ ticket.title }}
              </h4>
              <div class="flex justify-between items-center">
                <span class="text-[10px] text-gray-400 uppercase font-medium">{{ ticket.category }}</span>
                <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-[10px] font-bold text-gray-400">
                  {{ ticket.creator_id }}
                </div>
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
import { api } from '@/services/api';
import AppLayout from '@/layouts/AppLayout.vue';

const tickets = ref([]);
const showModal = ref(false);
const draggingTicketId = ref(null);
const dropTargetStatus = ref(null);
const isUpdatingStatus = ref(false);

const statuses = [
  { label: 'À traiter', value: 'Open' },
  { label: 'En cours', value: 'In Progress' },
  { label: 'Résolu', value: 'Resolved' },
  { label: 'Fermé', value: 'Closed' }
];

const getTicketsByStatus = (statusValue) => {
  return tickets.value.filter(t => t.status === statusValue);
};

const loadTickets = async () => {
  try {
    const response = await api.get('/tickets/');
    tickets.value = response.data;
  } catch (err) {
    console.error("Erreur lors du chargement des tickets", err);
  }
};

const onDragStart = (ticketId) => {
  draggingTicketId.value = ticketId;
};

const onDragEnd = () => {
  draggingTicketId.value = null;
  dropTargetStatus.value = null;
};

const onDragOver = (statusValue) => {
  dropTargetStatus.value = statusValue;
};

const onDragLeave = () => {
  dropTargetStatus.value = null;
};

const onDrop = async (targetStatus) => {
  if (draggingTicketId.value === null || isUpdatingStatus.value) {
    return;
  }

  const ticket = tickets.value.find((item) => item.id === draggingTicketId.value);
  if (!ticket) {
    onDragEnd();
    return;
  }

  if (ticket.status === targetStatus) {
    onDragEnd();
    return;
  }

  isUpdatingStatus.value = true;

  try {
    const response = await api.patch(`/tickets/${ticket.id}/status`, { status: targetStatus });

    const updatedTicket = response.data;
    tickets.value = tickets.value.map((item) =>
      item.id === updatedTicket.id ? updatedTicket : item
    );
  } catch (error) {
    console.error('Erreur lors du changement de statut', error);
    alert("Impossible de changer le statut du ticket.");
  } finally {
    isUpdatingStatus.value = false;
    onDragEnd();
  }
};

const maxTicketsInColumn = computed(() => {
  return Math.max(
    ...statuses.map(status => getTicketsByStatus(status.value).length)
  );
});

const columnHeight = computed(() => {
  const ticketHeight = 120;
  const padding = 100;

  return `${maxTicketsInColumn.value * ticketHeight + padding}px`;
});

onMounted(async () => {
  await loadTickets();
});
</script>