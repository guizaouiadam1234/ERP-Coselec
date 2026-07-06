<template>
  <AppLayout>
    <div class="min-h-screen bg-gray-50 p-8">
      <header class="mb-10 flex justify-between items-end">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Helpdesk</h1>
          <p class="text-sm text-gray-400 mt-1">Gestion des demandes internes</p>
        </div>
        
      </header>

      <div class="flex gap-8 items-start">
        <div v-for="status in statuses" :key="status.value" class="flex-1 flex flex-col">
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
              class="bg-white p-5 shadow-sm transition-all duration-300 hover:shadow-md cursor-default"
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
import { ref, onMounted } from 'vue';
import { api } from '@/services/api';
import AppLayout from '@/layouts/AppLayout.vue';

const tickets = ref([]);
const showModal = ref(false);

const statuses = [
  { label: 'À traiter', value: 'Open' },
  { label: 'En cours', value: 'In Progress' },
  { label: 'Résolu', value: 'Resolved' },
  { label: 'Fermé', value: 'Closed' }
];

const getTicketsByStatus = (statusValue) => {
  return tickets.value.filter(t => t.status === statusValue);
};

onMounted(async () => {
  try {
    const response = await api.get('/tickets/');
    tickets.value = response.data;
  } catch (err) {
    console.error("Erreur lors du chargement des tickets", err);
  }
});
</script>