<template>
  <div class="flex h-screen overflow-hidden">
    <Sidebar />
    <div class="flex-1 flex flex-col relative">
      <Navbar />
      <main class="flex-1 p-6 bg-gray-100 overflow-y-auto">
        <h1 class="text-2xl font-bold mb-4">Gestion des employés</h1>
        <button
          @click="showCreateModal = true"
          class="bg-[#d10f2f] text-white px-4 py-2 rounded-xl hover:bg-[#97091f] transition flex items-center gap-2 mb-6"
        >
          <span class="material-symbols-outlined">person_add</span>
          <span>Ajouter un employé</span>
        </button>

        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-red-50 text-left">
                <th class="px-6 py-4 text-sm font-semibold text-gray-700">Matricule</th>
                <th class="px-6 py-4 text-sm font-semibold text-gray-700">Employé</th>
                <th class="px-6 py-4 text-sm font-semibold text-gray-700">Email</th>
                <th class="px-6 py-4 text-sm font-semibold text-gray-700">Poste</th>
                <th class="px-6 py-4 text-sm font-semibold text-gray-700">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="employee in employees"
                :key="employee.id"
                @click="openEmployeeDetails(employee)"
                class="border-t hover:bg-red-50/50 transition cursor-pointer"
              >
                <td class="px-6 py-4 text-gray-600 font-medium">
                  {{ employee.matricule || 'EMP' + String(employee.id).padStart(3, "0") }}
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-red-100 text-[#d10f2f] flex items-center justify-center font-semibold">
                      {{ employee.first_name[0] }}
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">
                        {{ employee.first_name }} {{ employee.last_name }}
                      </p>
                      <p class="text-xs text-gray-500">
                        {{ employee.email }}
                      </p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-gray-500">{{ employee.email }}</td>
                <td class="px-6 py-4 text-gray-700">{{ employee.position }}</td>
                <td class="px-6 py-4">
                  <span :class="[getStatusClass(employee.status), 'px-3 py-1 rounded-full text-xs font-medium uppercase']">
                    {{ employee.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>

      <div 
        v-if="isSlideOverOpen" 
        @click="closeSlideOver"
        class="fixed inset-0 bg-black/20 z-40 transition-opacity backdrop-blur-sm"
      ></div>

      <div 
        class="fixed inset-y-0 right-0 z-50 w-full max-w-3xl bg-gray-50 shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col"
        :class="isSlideOverOpen ? 'translate-x-0' : 'translate-x-full'"
      >
        <div v-if="selectedEmployee" class="px-6 py-6 bg-white border-b border-gray-200 flex justify-between items-start shadow-sm z-10">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-full bg-red-100 text-[#d10f2f] flex items-center justify-center text-xl font-bold">
              {{ selectedEmployee.first_name[0] }}{{ selectedEmployee.last_name[0] }}
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ selectedEmployee.first_name }} {{ selectedEmployee.last_name }}</h2>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-sm text-gray-500 font-medium">{{ selectedEmployee.position }}</span>
                <span class="text-gray-300">•</span>
                <span :class="[getStatusClass(selectedEmployee.status), 'px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider']">
                  {{ selectedEmployee.status }}
                </span>
              </div>
            </div>
          </div>
          <button @click="closeSlideOver" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div v-if="selectedEmployee" class="flex-1 overflow-y-auto p-6 space-y-8">
          
          <section class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 border-b pb-2">Informations Générales</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs text-gray-500 uppercase">Matricule</p>
                <p class="font-medium text-gray-900">{{ selectedEmployee.matricule || 'Non défini' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase">Email professionnel</p>
                <p class="font-medium text-gray-900">{{ selectedEmployee.email }}</p>
              </div>
              </div>
          </section>

          <section class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <EmployeeContracts :employeeId="selectedEmployee.id" />
          </section>

          <section class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <EmployeeDocuments :employeeId="selectedEmployee.id" />
          </section>
        </div>
      </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import Sidebar from "../components/Sidebar.vue";
import Navbar from "../components/Navbar.vue";
import { getEmployees } from "@/services/employees";

// IMPORT DU SOUS-COMPOSANT
import EmployeeContracts from "@/components/employees/EmployeeContracts.vue";
import EmployeeDocuments from "@/components/employees/EmployeeDocuments.vue";

interface Employee {
  id: number;
  matricule: string;
  first_name: string;
  last_name: string;
  email: string;
  position: string;
  status: string;
}

const showCreateModal = ref(false);
const employees = ref<Employee[]>([]);

// --- GESTION DU VOLET LATÉRAL (SLIDE-OVER) ---
const isSlideOverOpen = ref(false);
const selectedEmployee = ref<Employee | null>(null);

const openEmployeeDetails = (employee: Employee) => {
  selectedEmployee.value = employee;
  // Petit délai optionnel pour la fluidité si beaucoup de données
  setTimeout(() => {
    isSlideOverOpen.value = true;
  }, 10);
};

const closeSlideOver = () => {
  isSlideOverOpen.value = false;
  // On attend la fin de l'animation CSS (300ms) pour vider l'employé
  setTimeout(() => {
    selectedEmployee.value = null;
  }, 300);
};
// ---------------------------------------------

const getStatusClass = (status: string) => {
  if (!status) return "bg-gray-100 text-gray-700";
  
  switch (status.toUpperCase()) {
    case "CDI":
    case "SUR SITE":
      return "bg-green-100 text-green-700";
    case "CDD":
    case "SUR CHANTIER":
      return "bg-orange-100 text-orange-700";
    case "STAGIAIRE":
      return "bg-blue-100 text-blue-700";
    case "EN CONGÉ":
    case "PRESTATAIRE":
      return "bg-purple-100 text-purple-700";
    case "INACTIF":
      return "bg-red-100 text-red-700";
    default:
      return "bg-gray-100 text-gray-700";
  }
};

onMounted(async () => {
  employees.value = await getEmployees();
});
</script>