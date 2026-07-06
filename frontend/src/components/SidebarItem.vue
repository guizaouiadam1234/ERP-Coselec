<script setup lang="ts">
import { RouterLink } from "vue-router";

defineProps<{
  to: string;
  icon: string;
  label: string;
  collapsed: boolean;
}>();
</script>

<template>
  <RouterLink
    :to="to"
    active-class="bg-white text-[#d10f2f] font-semibold shadow-lg"
    :class="[
      collapsed ? 'justify-center' : '',
      'group relative flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white hover:text-[#d10f2f] hover:font-semibold transition'
    ]"
  >
    <span class="material-symbols-outlined">
      {{ icon }}
    </span>

    <span v-if="!collapsed">
      {{ label }}
    </span>

    <span
      v-if="collapsed"
      class="tooltip"
    >
      {{ label }}
    </span>
  </RouterLink>
</template>

<style scoped>
.tooltip {
  position: absolute;
  left: 4.5rem;
  z-index: 9999;

  white-space: nowrap;

  padding: 0.5rem 0.75rem;

  background: white;
  color: #97091f;

  border-radius: 0.75rem;

  font-size: 0.875rem;
  font-weight: 500;

  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);

  opacity: 0;
  transform: translateX(10px);

  transition: all 0.2s ease;

  pointer-events: none;
}

.group:hover .tooltip {
  opacity: 1;
  transform: translateX(0);
}
</style>