<template>
  <div class="flex h-screen">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Navbar />
      <main class="flex-1 p-6 bg-gray-100 overflow-y-auto">
        <h1 class="text-2xl font-bold mb-4">Gestion des employés</h1>
        <button
  @click="showCreateModal = true"
  class="bg-[#d10f2f] text-white px-4 py-2 rounded-xl hover:bg-[#97091f] transition flex items-center gap-2"
>
  <span class="material-symbols-outlined">
    person_add
  </span>

  <span>
    Ajouter un employé
  </span>
</button>
        <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
  <table class="w-full">
    <thead>
      <tr class="bg-red-50 text-left">
        <th class="px-6 py-4 text-sm font-semibold text-gray-700">
          Matricule
        </th>

        <th class="px-6 py-4 text-sm font-semibold text-gray-700">
          Employé
        </th>

        <th class="px-6 py-4 text-sm font-semibold text-gray-700">
          Email
        </th>

        <th class="px-6 py-4 text-sm font-semibold text-gray-700">
          Poste
        </th>

        <th class="px-6 py-4 text-sm font-semibold text-gray-700">
          Statut
        </th>
      </tr>
    </thead>

    <tbody>
  <tr
    v-for="employee in employees"
    :key="employee.id"
    class="border-t hover:bg-gray-50 transition"
  >
    <td class="px-6 py-4 text-gray-600 font-medium">
      EMP{{ String(employee.id).padStart(3, "0") }}
    </td>

    <td class="px-6 py-4">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full bg-red-100 text-[#d10f2f] flex items-center justify-center font-semibold"
        >
          {{ employee.first_name[0] }}
        </div>

        <div>
          <p class="font-medium text-gray-900">
            {{ employee.first_name }}
            {{ employee.last_name }}
          </p>

          <p class="text-xs text-gray-500">
            {{ employee.email }}
          </p>
        </div>
      </div>
    </td>

    <td class="px-6 py-4 text-gray-500">
      {{ employee.email }}
    </td>

    <td class="px-6 py-4 text-gray-700">
      {{ employee.position }}
    </td>

    <td class="px-6 py-4">
      <span
        :class="[
          getStatusClass(employee.status),
          'px-3 py-1 rounded-full text-sm font-medium'
        ]"
      >
        {{ employee.status }}
      </span>
    </td>
  </tr>
</tbody>
  </table>
</div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from "../components/Sidebar.vue";
import Navbar from "../components/Navbar.vue";


import { onMounted, ref } from "vue";
import { getEmployees } from "@/services/employees";

const showCreateModal = ref(false);

interface Employee {
  id: number;
  matricule: string;
  first_name: string;
  last_name: string;
  email: string;
  position: string;
  status: string;
}

const getStatusClass = (status: string) => {
  switch (status.toUpperCase()) {
    case "CDI":
      return "bg-green-100 text-green-700";

    case "CDD":
      return "bg-orange-100 text-orange-700";

    case "STAGIAIRE":
      return "bg-blue-100 text-blue-700";

    case "PRESTATAIRE":
      return "bg-purple-100 text-purple-700";

    case "INACTIF":
      return "bg-red-100 text-red-700";

    default:
      return "bg-gray-100 text-gray-700";
  }
};


const employees = ref<Employee[]>([]);

onMounted(async () => {
  employees.value = await getEmployees();
});

</script>