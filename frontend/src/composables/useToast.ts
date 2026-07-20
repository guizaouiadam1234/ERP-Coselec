import { ref } from 'vue';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useToast() {
  const addToast = (message: string, type: ToastType = 'info', durationMs = 4000) => {
    const id = nextId++;
    toasts.value.push({ id, message, type });

    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id);
    }, durationMs);
  };

  const success = (message: string) => addToast(message, 'success');
  const error = (message: string) => addToast(message, 'error', 5000);
  const info = (message: string) => addToast(message, 'info');

  const dismiss = (id: number) => {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  };

  return { toasts, addToast, success, error, info, dismiss };
}
