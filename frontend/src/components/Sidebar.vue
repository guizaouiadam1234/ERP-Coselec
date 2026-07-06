<script setup lang="ts">
import { ref } from "vue";

import SidebarItem from "./SidebarItem.vue";

const collapsed = ref(false);

const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};
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
      <!-- Tableau de bord -->
      <div>
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Tableau de bord
        </h2>

        <SidebarItem
          to="/home"
          icon="dashboard"
          label="Dashboard"
          :collapsed="collapsed"
        />
      </div>

      <!-- RH -->
      <div>
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
          to="/approvals"
          icon="check_circle"
          label="Validations"
          :collapsed="collapsed"
        />
      </div>

      <!-- Projets -->
      <div>
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Projets
        </h2>

        <SidebarItem
          to="/projects"
          icon="folder"
          label="Projets"
          :collapsed="collapsed"
        />
      </div>

      <!-- Stock -->
      <div>
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
      </div>

      <!-- Documents -->
      <div>
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Documents
        </h2>

        <SidebarItem
          to="/documents"
          icon="description"
          label="GED"
          :collapsed="collapsed"
        />
      </div>

      <!-- Administration -->
      <div>
        <h2
          v-if="!collapsed"
          class="text-xs uppercase text-red-200 mb-2"
        >
          Administration
        </h2>

        <SidebarItem
          to="/users"
          icon="person"
          label="Utilisateurs"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/roles"
          icon="vpn_key"
          label="Rôles"
          :collapsed="collapsed"
        />

        <SidebarItem
          to="/permissions"
          icon="shield"
          label="Permissions"
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