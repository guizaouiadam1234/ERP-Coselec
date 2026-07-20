<script setup lang="ts">
import { useToast } from '@/composables/useToast';

const { toasts, dismiss } = useToast();

const bgClass = (type: string) => {
  switch (type) {
    case 'success': return 'bg-green-600';
    case 'error': return 'bg-red-600';
    default: return 'bg-gray-800';
  }
};

const iconName = (type: string) => {
  switch (type) {
    case 'success': return 'check_circle';
    case 'error': return 'error';
    default: return 'info';
  }
};
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="bgClass(toast.type)"
          class="pointer-events-auto flex items-center gap-3 rounded-xl px-5 py-3.5 text-white shadow-xl min-w-[300px] max-w-md cursor-pointer"
          @click="dismiss(toast.id)"
        >
          <span class="material-symbols-outlined text-xl shrink-0">{{ iconName(toast.type) }}</span>
          <span class="text-sm font-medium leading-snug">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-leave-active {
  transition: all 0.25s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(80px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(80px) scale(0.95);
}
</style>
