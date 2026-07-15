<!-- GanttView.vue -->
<template>
  <div class="gantt-container w-full overflow-x-auto bg-white p-4 rounded-lg shadow-sm border">
    <g-gantt-chart
      v-if="ganttBars.length > 0"
      :chart-start="chartStart"
      :chart-end="chartEnd"
      precision="day"
      bar-start="start_date"
      bar-end="due_date"
      color-scheme="creamy"
      :grid="true"
      width="100%"
      @dragend-bar="onDragEndBar"
    >
      <g-gantt-row label="Tâches" :bars="ganttBars" />
    </g-gantt-chart>
    <div v-else class="text-center text-gray-400 py-6">
      Aucune tâche planifiée à afficher dans le diagramme.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import {
  GGanttChart,
  GGanttRow,
  type GanttBarObject,
} from '@infectoone/vue-ganttastic';

const props = defineProps<{
  tasks: Array<{
    id: number;
    title: string;
    status?: string | null;
    start_date?: string | null;
    due_date?: string | null;
    created_at?: string | null;
  }>;
}>();

const emit = defineEmits<{
  (e: 'update-task', taskId: number, data: any): void;
}>();

// Formatter guaranteeing YYYY-MM-DD HH:mm required by Ganttastic / Day.js
const formatDateString = (date: Date) => {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} 00:00`;
};

const todayStr = formatDateString(new Date());

const parseToCleanDate = (value?: string | null): Date | null => {
  if (!value) return null;
  const d = new Date(value);
  return isNaN(d.getTime()) ? null : d;
};

const ganttBars = computed<GanttBarObject[]>(() => {
  if (!props.tasks || !Array.isArray(props.tasks)) return [];

  return props.tasks.map((task) => {
    // Attempt parsing dates cleanly
    const startParsed = parseToCleanDate(task.start_date) || parseToCleanDate(task.created_at) || new Date();
    let dueParsed = parseToCleanDate(task.due_date) || new Date(startParsed);

    // Enforce that due_date is mathematically equal or greater than start_date
    if (dueParsed.getTime() < startParsed.getTime()) {
      dueParsed = new Date(startParsed.getTime());
    }

    return {
      start_date: formatDateString(startParsed),
      due_date: formatDateString(dueParsed),
      ganttBarConfig: {
        id: String(task.id),
        label: task.title || 'Sans titre',
        hasHandles: true,
        style: {
          background: task.status === 'A faire' || task.status == 'TO DO'? "#6577c2" : task.status === 'Terminée' || task.status === 'DONE' ? '#15803d' : task.status === 'En cours' || task.status === 'IN_PROGRESS' ? '#ea580c' : '#b91c1c',
          borderRadius: '8px',
          color: '#fff',
        },
      },
    };
  });
});

const chartStart = computed(() => {
  if (!ganttBars.value.length) return todayStr;
  const times = ganttBars.value.map(b => new Date(b.start_date.replace(' 00:00', '')).getTime());
  const minTime = Math.min(...times);
  return formatDateString(new Date(minTime));
});

const chartEnd = computed(() => {
  if (!ganttBars.value.length) {
    const tom = new Date();
    tom.setDate(tom.getDate() + 1);
    return formatDateString(tom);
  }
  
  const times = ganttBars.value.map(b => new Date(b.due_date.replace(' 00:00', '')).getTime());
  const maxTime = Math.max(...times);
  const targetEnd = new Date(maxTime);

  if (formatDateString(targetEnd) === chartStart.value) {
    targetEnd.setDate(targetEnd.getDate() + 1);
  }
  
  return formatDateString(targetEnd);
});

const onDragEndBar = ({ bar }: { bar: GanttBarObject }) => {
  emit('update-task', Number(bar.ganttBarConfig.id), {
    start_date: bar.start_date,
    due_date: bar.due_date,
  });
};
</script>