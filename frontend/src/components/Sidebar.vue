<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import SidebarItem from "./SidebarItem.vue";
import {
  getStoredProfile,
  hasAnyRole,
  refreshCurrentUserProfile,
  type CurrentUserProfile,
} from "@/services/session";

const collapsed = ref(false);
const profile = ref<CurrentUserProfile | null>(getStoredProfile());

const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};

const roles = computed(() => profile.value?.roles || []);

const canViewHr = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "RH", "Direction"]);
});

const canViewStock = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "Stock / Logistique", "Direction", "Finance"]);
});

const canViewDocuments = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "Direction", "Finance"]);
});
const canViewProjects = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "Responsable Projet", "Direction"]);
});

const canViewAdmin = computed(() => {
  return hasAnyRole(roles.value, ["Admin"]);
});

const canViewItRequests = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "IT"]);
});

const canViewFacilityRequests = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "Facility", "Logistique", "Direction", "Finance"]);
});

const canViewFuelRequests = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "Facility", "Logistique", "Direction", "Finance"]);
});

const canViewHrRequests = computed(() => {
  return hasAnyRole(roles.value, ["Admin", "RH", "Direction"]);
});

onMounted(async () => {
  try {
    profile.value = await refreshCurrentUserProfile();
  } catch {
    profile.value = getStoredProfile();
  }
});
</script>

<template>
  <aside
    :class="[
      collapsed ? 'w-20' : 'w-72',
      'sidebar h-screen overflow-y-auto bg-gradient-to-b from-[#d10f2f] to-[#97091f] text-white flex-shrink-0 transition-all duration-300'
    ]"
  >
    <!-- Header -->
    <div
      class="p-6 border-b border-white/10 flex items-center justify-between"
    >
      <h1
        v-if="!collapsed"
        class="text-2xl font-bold whitespace-nowrap"
      >
        COSELEC ERP
      </h1>

      <div
        v-else
        class="w-full flex justify-center text-2xl font-bold"
      >
        C
      </div>

      <button
        @click="toggleSidebar"
        class="p-2 rounded-lg hover:bg-white/10 transition"
      >
        <span class="material-symbols-outlined">
          menu
        </span>
      </button>
    </div>

    <nav class="p-4 space-y-6">
     
      <!-- RH -->
      <div v-if="canViewHr">
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Ressources Humaines
        </h2>

        <SidebarItem
          to="/employees"
          icon="people"
          label="Employés"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/departments"
          icon="apartment"
          label="Départements"
          :collapsed="collapsed"
        />
      </div>

      <!-- Demandes -->
      <div>
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Demandes
        </h2>

        <SidebarItem
          to="/requests"
          icon="assignment"
          label="Mes demandes"
          :collapsed="collapsed"
        />

        <SidebarItem
          v-if="canViewItRequests"
          to="/it-requests"
          icon="memory"
          label="Tickets IT"
          :collapsed="collapsed"
        />

        <SidebarItem
          v-if="canViewFacilityRequests"
          to="/facility-requests"
          icon="home_repair_service"
          label="Tickets Logistique"
          :collapsed="collapsed"
        />

        <SidebarItem
          v-if="canViewFuelRequests"
          to="/fuel-requests"
          icon="local_gas_station"
          label="Demandes Carburant"
          :collapsed="collapsed"
        />

        <SidebarItem
          v-if="canViewHrRequests"
          to="/hr-requests"
          icon="groups"
          label="Demandes RH"
          :collapsed="collapsed"
        />
      </div>


      <!-- Stock -->
      <div v-if="canViewStock">
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Stock
        </h2>

        <SidebarItem
          to="/stock"
          icon="inventory_2"
          label="Vue d'ensemble"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/stock/movement"
          icon="sync_alt"
          label="Mouvements"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/stock/canvas"
          icon="view_kanban"
          label="Canvas"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/stock-reservations"
          icon="event_seat"
          label="Réservations"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/procurement"
          icon="shopping_cart"
          label="Achats"
          :collapsed="collapsed"
        />
      </div>

      <div v-if="canViewProjects">
        <h2 class = "text-xs uppercase text-red-200 mb-2">Projets</h2>
        <SidebarItem to="/project-dashboard" icon="dashboard" label="Dashboard Projet" :collapsed="collapsed"></SidebarItem>
        <SidebarItem to="/projects" icon="work" label="Projets" :collapsed="collapsed"></SidebarItem>
        <SidebarItem to="/portfolio" icon="pie_chart" label="Portfolio" :collapsed="collapsed"></SidebarItem>
        <SidebarItem to="/project-budget" icon="account_balance_wallet" label="Budgets" :collapsed="collapsed"></SidebarItem>
      </div>

      <!-- Documents -->
      <div v-if="canViewDocuments">
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Documents
        </h2>

        <SidebarItem
          to="/caisse"
          icon="receipt_long"
          label="Pièce de Caisse"
          :collapsed="collapsed"
        />
      </div>

      <!-- Admin -->
      <div v-if="canViewAdmin">
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Admin
        </h2>

        <SidebarItem
          to="/admin/users"
          icon="admin_panel_settings"
          label="Gestion des utilisateurs"
          :collapsed="collapsed"
        />
      </div>

      
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  scrollbar-width: none;
}

.sidebar::-webkit-scrollbar {
  display: none;
}
</style>