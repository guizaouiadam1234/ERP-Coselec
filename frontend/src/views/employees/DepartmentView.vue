<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import api from '@/services/api';

interface Department {
  id: number;
  name: string;
}

interface WeekDay {
  label: string;
  date: string;
  fullDate: string;
}

interface EmployeeSchedule {
  id: number;
  name: string;
  role: string;
  department_id: number;
  schedule: Array<'CHANTIER' | 'SITE' | 'CONGE' | 'NONE'>;
}

const isLoading = ref<boolean>(false);
const selectedDepartment = ref<string>('');
const employees = ref<EmployeeSchedule[]>([]);

// Timeline Control States - Defaulting to current week base
const currentDateCursor = ref<string>('2026-07-06'); 
const daysViewWindow = ref<number>(7); 

const departments = ref<Department[]>([
  { id: 1, name: 'Département A' },
  { id: 2, name: 'Département B' },
  { id: 3, name: 'Département C' }
]);

const currentWeekDays = ref<WeekDay[]>([]);

const calculateGridHeaders = (startDateStr: string, count: number): void => {
  const start = new Date(startDateStr);
  const days: WeekDay[] = [];
  const labels: string[] = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
  
  for (let i = 0; i < count; i++) {
    const nextDate = new Date(start);
    nextDate.setDate(start.getDate() + i);
    
    const dayFormatter = nextDate.getDate().toString().padStart(2, '0');
    const monthFormatter = (nextDate.getMonth() + 1).toString().padStart(2, '0');
    const yearFormatter = nextDate.getFullYear();
    
    const dayLabel = labels[nextDate.getDay()] as string;

    days.push({
      label: dayLabel,
      date: `${dayFormatter}/${monthFormatter}`,
      fullDate: `${yearFormatter}-${monthFormatter}-${dayFormatter}`
    });
  }
  currentWeekDays.value = days;
};

const fetchHRData = async (): Promise<void> => {
  isLoading.value = true;
  calculateGridHeaders(currentDateCursor.value, daysViewWindow.value);
  
  try {
    const res = await api.get(`/hr/schedule-matrix`, {
      params: {
        start_date: currentDateCursor.value,
        days_count: daysViewWindow.value
      }
    });
    employees.value = res.data;
  } catch (error) {
    console.error("Erreur d'initialisation du planning RH", error);
    // Anonymized fallback state layout values
    employees.value = [
      { id: 1, name: 'Collaborateur A', role: 'Rôle A', department_id: 1, schedule: ['CHANTIER', 'CHANTIER', 'SITE', 'CHANTIER', 'CHANTIER', 'NONE', 'NONE'] },
      { id: 2, name: 'Collaborateur B', role: 'Rôle B', department_id: 3, schedule: ['SITE', 'SITE', 'CONGE', 'CONGE', 'CONGE', 'NONE', 'NONE'] },
      { id: 3, name: 'Collaborateur C', role: 'Rôle C', department_id: 1, schedule: ['CHANTIER', 'CHANTIER', 'CHANTIER', 'CHANTIER', 'CHANTIER', 'NONE', 'NONE'] },
      { id: 4, name: 'Collaborateur D', role: 'Rôle D', department_id: 2, schedule: ['SITE', 'CHANTIER', 'SITE', 'CHANTIER', 'SITE', 'NONE', 'NONE'] }
    ];
  } finally {
    isLoading.value = false;
  }
};

const shiftTimeline = (daysOffset: number): void => {
  const current = new Date(currentDateCursor.value);
  current.setDate(current.getDate() + daysOffset);
  
  const yyyy = current.getFullYear();
  const mm = (current.getMonth() + 1).toString().padStart(2, '0');
  const dd = current.getDate().toString().padStart(2, '0');
  
  currentDateCursor.value = `${yyyy}-${mm}-${dd}`;
};

const setToday = (): void => {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = (today.getMonth() + 1).toString().padStart(2, '0');
  const dd = today.getDate().toString().padStart(2, '0');
  currentDateCursor.value = `${yyyy}-${mm}-${dd}`;
};

watch([currentDateCursor, daysViewWindow], () => {
  fetchHRData();
});

const getStatusClasses = (status: 'CHANTIER' | 'SITE' | 'CONGE' | 'NONE'): string => {
  switch (status) {
    case 'CHANTIER': return 'bg-red-600 text-white border-red-700 font-semibold shadow-3xs';
    case 'SITE': return 'bg-gray-800 text-white border-gray-900 font-semibold shadow-3xs';
    case 'CONGE': return 'bg-amber-400 text-gray-900 border-amber-500 font-bold shadow-3xs';
    default: return 'bg-gray-100 text-gray-400 border-gray-200 font-normal';
  }
};

const getStatusLabel = (status: 'CHANTIER' | 'SITE' | 'CONGE' | 'NONE'): string => {
  if (status === 'CHANTIER') return 'Chantier';
  if (status === 'SITE') return 'Sur Site';
  if (status === 'CONGE') return 'Congé';
  return '-';
};

onMounted(() => {
  fetchHRData();
});
</script>

<template>
  <AppLayout>
    <div class="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen font-sans">
      
      <!-- Top Header Row -->
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between border-b border-gray-200 pb-5 mb-6 bg-white p-4 rounded-xl shadow-xs gap-4">
        <div class="flex items-center space-x-3">
          <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m0 4h3m-3 0H5m3 14v-4m0 0H5m3 0h3m-3A1 1 0 007 9v11a1 1 0 001 1h8a1 1 0 001-1V9a1 1 0 00-1-1H8z" />
          </svg>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Planning d'Affectation</h1>
            <p class="text-sm text-gray-500">Vue globale des déploiements opérationnels de l'entreprise</p>
          </div>
        </div>

        <!-- Legend -->
        <div class="flex flex-wrap items-center gap-4 text-xs bg-gray-50 p-2.5 rounded-lg border border-gray-200">
          <div class="flex items-center space-x-1.5">
            <span class="w-3 h-3 bg-red-600 rounded-sm inline-block"></span>
            <span class="font-semibold text-gray-700">En Chantier</span>
          </div>
          <div class="flex items-center space-x-1.5">
            <span class="w-3 h-3 bg-gray-800 rounded-sm inline-block"></span>
            <span class="font-semibold text-gray-700">Sur Site (Bureau)</span>
          </div>
          <div class="flex items-center space-x-1.5">
            <span class="w-3 h-3 bg-amber-400 rounded-sm inline-block"></span>
            <span class="font-semibold text-gray-700">Congé Payé</span>
          </div>
        </div>
      </div>

      <!-- Main Table Card -->
      <div class="bg-white border border-gray-200 rounded-xl shadow-xs overflow-hidden">
        
        <!-- Controls Navigation Row Header -->
        <div class="bg-gray-50 border-b border-gray-200 px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex items-center space-x-4 flex-wrap gap-2">
            <select v-model="selectedDepartment" class="border border-gray-300 rounded-lg bg-white px-3 py-1.5 text-xs text-gray-700 focus:outline-none focus:border-red-500 cursor-pointer">
              <option value="">Tous les pôles</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
            </select>

            <select v-model.number="daysViewWindow" class="border border-gray-300 rounded-lg bg-white px-3 py-1.5 text-xs text-gray-700 focus:outline-none focus:border-red-500 cursor-pointer">
              <option :value="7">Vue 1 Semaine</option>
              <option :value="14">Vue 2 Semaines</option>
            </select>
          </div>

          <div class="flex items-center space-x-2 self-end md:self-auto">
            <button @click="shiftTimeline(-daysViewWindow)" class="p-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-100 text-gray-600 flex items-center transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
              </svg>
            </button>

            <input 
              type="date" 
              v-model="currentDateCursor" 
              class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm text-gray-800 bg-white focus:outline-none font-medium cursor-pointer"
            />

            <button @click="setToday" class="px-4 py-1.5 border border-gray-300 rounded-lg bg-white text-sm text-gray-700 font-medium hover:bg-gray-100 transition-colors">
              Aujourd'hui
            </button>

            <button @click="shiftTimeline(daysViewWindow)" class="p-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-100 text-gray-600 flex items-center transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Matrix Calendar Table Grid -->
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse table-fixed min-w-[800px]">
            <thead>
              <tr class="bg-gray-50 border-b border-gray-200 text-gray-500 uppercase text-xxs tracking-wider font-bold h-12">
                <th class="px-6 py-2 font-bold text-gray-700 w-64 sticky left-0 bg-gray-50 z-10 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">Collaborateurs</th>
                <th v-for="day in currentWeekDays" :key="day.fullDate" class="px-2 py-2 text-center border-l border-gray-200/40">
                  <div class="text-gray-900 text-xs font-bold leading-none">{{ day.label }}</div>
                  <div class="text-xxs font-medium mt-1 text-gray-400">{{ day.date }}</div>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 text-sm text-gray-700">
              <tr v-for="emp in employees" :key="emp.id" class="hover:bg-gray-50/40 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap border-r border-gray-200 sticky left-0 bg-white z-10 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-red-100 text-red-700 font-bold text-xs rounded-full flex items-center justify-center uppercase">
                      {{ emp.name.substring(0, 2) }}
                    </div>
                    <div>
                      <span class="block text-sm font-bold text-gray-800">{{ emp.name }}</span>
                      <span class="block text-xxs text-gray-400 font-medium mt-0.5">{{ emp.role }}</span>
                    </div>
                  </div>
                </td>

                <td v-for="(status, index) in emp.schedule" :key="index" class="p-1 border-l border-gray-100 text-center align-middle whitespace-nowrap">
                  <div 
                    :class="getStatusClasses(status)"
                    class="mx-auto rounded-xl py-2 text-xxs border uppercase tracking-wider font-bold min-h-[32px] flex items-center justify-center max-w-[90px]"
                  >
                    {{ getStatusLabel(status) }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppLayout>
</template>