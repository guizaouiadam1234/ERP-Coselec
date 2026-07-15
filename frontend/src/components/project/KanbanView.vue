<template>
  <div class="kanban-board">
    <div
      v-for="column in columns"
      :key="column.status"
      class="kanban-column"
    >
      <h3>{{ column.label }}</h3>
      <draggable
        v-model="column.tasks"
        group="tasks"
        class="task-list"
        item-key="id"
        @end="onDragEnd(column.status)"
      >
        <template #item="{ element: task }">
          <div class="task-card">
            <p>{{ task.title }}</p>
            <small>{{ task.priority }}</small>
          </div>
        </template>
      </draggable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import draggable from 'vuedraggable';

const props = defineProps<{
  tasks: any[];
}>();

const emit = defineEmits<{
  (e: 'update-task', taskId: number, data: any): void;
}>();

// Map frontend labels to backend status values
const statusMap = {
  'A faire': 'TODO',
  'En cours': 'IN_PROGRESS',
  'Revue': 'REVIEW',
  'Terminée': 'DONE'
};

// Define columns with labels and a tasks array
const columns = ref(
  Object.entries(statusMap).map(([label, status]) => ({
    status,
    label,
    tasks: [] as any[]
  }))
);

// Populate columns from props.tasks
watch(
  () => props.tasks,
  (newTasks) => {
    const grouped: Record<string, any[]> = {};
    newTasks.forEach(t => {
      const st = t.status || 'TODO';
      if (!grouped[st]) grouped[st] = [];
      grouped[st].push(t);
    });
    columns.value.forEach(col => {
      col.tasks = grouped[col.status] || [];
    });
  },
  { immediate: true, deep: true }
);

// Called when a drag ends
const onDragEnd = (newStatus: string) => {
  const column = columns.value.find(c => c.status === newStatus);
  if (!column || column.tasks.length === 0) return;

  // The moved task is the last one in the list (because draggable appends)
  const moved = column.tasks[column.tasks.length - 1];
  if (!moved || moved.status === newStatus) return;

  // Emit update so parent can save to API
  emit('update-task', moved.id, { status: newStatus });
};
</script>

<style scoped>
.kanban-board {
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  padding: 1rem 0;
}
.kanban-column {
  flex: 0 0 280px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}
.kanban-column h3 {
  margin-top: 0;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6c757d;
}
.task-list {
  min-height: 100px;
}
.task-card {
  background: white;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  cursor: grab;
}
.task-card p {
  margin: 0 0 0.25rem 0;
  font-weight: 500;
}
.task-card small {
  color: #6c757d;
}
</style>