<template>
  <div class="gantt-container">
    <v-gantt
      :tasks="ganttTasks"
      :options="options"
      @update-task="onUpdateTask"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { VGantt, type GanttTask } from 'vue-ganttastic';
import 'vue-ganttastic/style.css';

const props = defineProps<{
  tasks: any[];
}>();

const emit = defineEmits<{
  (e: 'update-task', taskId: number, data: any): void;
}>();

const ganttTasks = computed<GanttTask[]>(() =>
  props.tasks.map((task) => ({
    id: task.id,
    name: task.title,
    start: task.start_date || task.created_at?.split('T')[0] || new Date().toISOString().split('T')[0],
    end: task.due_date,
    progress: task.status === 'Terminée' ? 100 : task.status === 'En cours' ? 50 : 0,
  }))
);

const options = {
  columns: ['name', 'start', 'end', 'progress'],
  timeScale: { unit: 'day', step: 1 },
};

const onUpdateTask = (updated: GanttTask) => {
  emit('update-task', updated.id, {
    start_date: updated.start,
    due_date: updated.end,
  });
};
</script>