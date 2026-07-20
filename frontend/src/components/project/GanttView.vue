<!-- GanttView.vue -->
<template>
  <div class="gantt-wrapper">
    <!-- Gantt chart -->
    <div class="gantt-container" ref="ganttContainerRef">
      <g-gantt-chart
        v-if="ganttRows.length > 0"
        :chart-start="visibleStart"
        :chart-end="visibleEnd"
        precision="day"
        bar-start="start_date"
        bar-end="due_date"
        color-scheme="creamy"
        :grid="true"
        :width="chartWidth"
        @dragend-bar="onDragEndBar"
      >
        <g-gantt-row
          v-for="(row, index) in ganttRows"
          :key="`gantt-row-${index}`"
          :label="row.label"
          :bars="row.bars"
        >
          <template #bar-label="{ bar }">
            <div
              class="gantt-bar-inner"
              @mouseenter="showTooltip($event, bar)"
              @mouseleave="hideTooltip"
              @mousemove="moveTooltip($event)"
            >
              <span class="bar-text">{{ bar.ganttBarConfig.label }}</span>
            </div>
          </template>
        </g-gantt-row>
      </g-gantt-chart>
      <div v-else class="empty-state">
        Aucune tâche planifiée à afficher dans le diagramme.
      </div>
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible"
        class="gantt-tooltip"
        :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
      >
        <div class="tooltip-title">{{ tooltip.label }}</div>
        <div class="tooltip-dates">
          <span>📅 {{ tooltip.start }} → {{ tooltip.end }}</span>
        </div>
        <div class="tooltip-status" :style="{ color: tooltip.statusColor }">
          {{ tooltip.status }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue';
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

// ── Zoom ──────────────────────────────────────────────────────
const zoomLevels = [
  { label: '1 semaine', days: 7 },
  { label: '2 semaines', days: 14 },
  { label: '1 mois', days: 30 },
  { label: '2 mois', days: 60 },
  { label: '3 mois', days: 90 },
  { label: '6 mois', days: 180 },
  { label: 'Tout', days: 0 },
];
const zoomIndex = ref(6); // Default: show all
const zoomLevelLabel = computed(() => zoomLevels[zoomIndex.value].label);

const zoomIn = () => { if (zoomIndex.value > 0) zoomIndex.value--; };
const zoomOut = () => { if (zoomIndex.value < zoomLevels.length - 1) zoomIndex.value++; };
const zoomReset = () => { zoomIndex.value = 6; };

// ── Chart width (increases when zoomed in for scrollability) ──
const chartWidth = computed(() => {
  const level = zoomLevels[zoomIndex.value];
  if (level.days === 0) return '100%';
  // Make the chart wider when zoomed so bars are bigger
  const totalDays = dataDaySpan.value;
  if (totalDays <= 0) return '100%';
  const ratio = totalDays / level.days;
  return ratio > 1 ? `${Math.max(100, Math.round(ratio * 100))}%` : '100%';
});

// ── Date utils ────────────────────────────────────────────────
const formatDateString = (date: Date) => {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} 00:00`;
};

const formatFR = (dateStr: string) => {
  const d = new Date(dateStr.replace(' 00:00', ''));
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
};

const todayStr = formatDateString(new Date());

const parseToCleanDate = (value?: string | null): Date | null => {
  if (!value) return null;
  const d = new Date(value);
  return isNaN(d.getTime()) ? null : d;
};

// ── Bar colors ────────────────────────────────────────────────
const statusColor = (status?: string | null): string => {
  if (!status) return '#6577c2';
  const s = status.toLowerCase();
  if (s.includes('terminé') || s === 'done') return '#15803d';
  if (s.includes('en cours') || s === 'in_progress') return '#ea580c';
  if (s.includes('revue') || s === 'review') return '#d97706';
  if (s.includes('a faire') || s === 'to do' || s === 'todo') return '#6577c2';
  return '#b91c1c';
};

// ── Bars ──────────────────────────────────────────────────────
const ganttBars = computed<GanttBarObject[]>(() => {
  if (!props.tasks || !Array.isArray(props.tasks)) return [];

  return props.tasks.map((task) => {
    const startParsed = parseToCleanDate(task.start_date) || parseToCleanDate(task.created_at) || new Date();
    let dueParsed = parseToCleanDate(task.due_date) || new Date(startParsed);

    // Min 1-day bar for visibility
    if (dueParsed.getTime() <= startParsed.getTime()) {
      dueParsed = new Date(startParsed.getTime() + 86400000);
    }

    const bg = statusColor(task.status);

    return {
      start_date: formatDateString(startParsed),
      due_date: formatDateString(dueParsed),
      _taskStatus: task.status || '',
      ganttBarConfig: {
        id: String(task.id),
        label: task.title || 'Sans titre',
        hasHandles: true,
        style: {
          background: bg,
          borderRadius: '6px',
          color: '#fff',
          fontSize: '11px',
          fontWeight: '600',
          minWidth: '18px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          padding: '0 6px',
          cursor: 'pointer',
        },
      },
    };
  });
});

// ── Rows (cascade layout) ────────────────────────────────────
const ganttRows = computed(() => {
  if (!ganttBars.value.length) return [] as Array<{ label: string; bars: GanttBarObject[] }>;

  const sortedBars = [...ganttBars.value].sort((a, b) => {
    const aStart = new Date(String(a.start_date).replace(' 00:00', '')).getTime();
    const bStart = new Date(String(b.start_date).replace(' 00:00', '')).getTime();
    return aStart - bStart;
  });

  const rowLastEnd: number[] = [];
  const rows: Array<{ label: string; bars: GanttBarObject[] }> = [];

  for (const bar of sortedBars) {
    const startTime = new Date(String(bar.start_date).replace(' 00:00', '')).getTime();
    const endTime = new Date(String(bar.due_date).replace(' 00:00', '')).getTime();

    let targetRow = rowLastEnd.findIndex((lastEnd) => startTime >= lastEnd);

    if (targetRow === -1) {
      targetRow = rows.length;
      rows.push({ label: `Ligne ${targetRow + 1}`, bars: [] });
      rowLastEnd.push(endTime);
    } else {
      rowLastEnd[targetRow] = endTime;
    }

    rows[targetRow]?.bars.push(bar);
  }

  return rows;
});

// ── Chart date range ─────────────────────────────────────────
const dataMinTime = computed(() => {
  if (!ganttBars.value.length) return new Date().getTime();
  return Math.min(...ganttBars.value.map(b => new Date(String(b.start_date).replace(' 00:00', '')).getTime()));
});

const dataMaxTime = computed(() => {
  if (!ganttBars.value.length) return new Date().getTime() + 86400000;
  return Math.max(...ganttBars.value.map(b => new Date(String(b.due_date).replace(' 00:00', '')).getTime()));
});

const dataDaySpan = computed(() => {
  return Math.ceil((dataMaxTime.value - dataMinTime.value) / 86400000);
});

const visibleStart = computed(() => {
  const level = zoomLevels[zoomIndex.value];
  if (level.days === 0) {
    // Show all: add 2-day padding
    const d = new Date(dataMinTime.value);
    d.setDate(d.getDate() - 2);
    return formatDateString(d);
  }
  // Center zoom on today
  const today = new Date();
  const halfDays = Math.floor(level.days / 2);
  const start = new Date(today);
  start.setDate(start.getDate() - halfDays);
  // Don't go before data start
  const dataStart = new Date(dataMinTime.value);
  dataStart.setDate(dataStart.getDate() - 2);
  return formatDateString(start < dataStart ? dataStart : start);
});

const visibleEnd = computed(() => {
  const level = zoomLevels[zoomIndex.value];
  if (level.days === 0) {
    const d = new Date(dataMaxTime.value);
    d.setDate(d.getDate() + 2);
    return formatDateString(d);
  }
  const today = new Date();
  const halfDays = Math.ceil(level.days / 2);
  const end = new Date(today);
  end.setDate(end.getDate() + halfDays);
  const dataEnd = new Date(dataMaxTime.value);
  dataEnd.setDate(dataEnd.getDate() + 2);
  return formatDateString(end > dataEnd ? dataEnd : end);
});

// ── Tooltip ──────────────────────────────────────────────────
const tooltip = reactive({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  start: '',
  end: '',
  status: '',
  statusColor: '',
});

const showTooltip = (event: MouseEvent, bar: GanttBarObject) => {
  tooltip.label = bar.ganttBarConfig.label || '';
  tooltip.start = formatFR(String(bar.start_date));
  tooltip.end = formatFR(String(bar.due_date));
  tooltip.status = (bar as any)._taskStatus || '';
  tooltip.statusColor = statusColor(tooltip.status);
  tooltip.x = event.clientX + 14;
  tooltip.y = event.clientY - 50;
  tooltip.visible = true;
};

const moveTooltip = (event: MouseEvent) => {
  tooltip.x = event.clientX + 14;
  tooltip.y = event.clientY - 50;
};

const hideTooltip = () => {
  tooltip.visible = false;
};

// ── Drag ─────────────────────────────────────────────────────
const onDragEndBar = (payload: { bar?: GanttBarObject; movedBars?: Map<GanttBarObject, { oldStart: unknown; oldEnd: unknown }> }) => {
  const moved = payload?.movedBars instanceof Map && payload.movedBars.size > 0
    ? Array.from(payload.movedBars.keys())
    : payload?.bar
      ? [payload.bar]
      : [];

  moved.forEach((bar) => {
    emit('update-task', Number(bar.ganttBarConfig.id), {
      start_date: bar.start_date,
      due_date: bar.due_date,
      source: 'gantt',
    });
  });
};
</script>

<style scoped>
.gantt-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}

.gantt-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 8px 16px;
  background: #fafbfc;
  border-bottom: 1px solid #e5e7eb;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.zoom-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #374151;
  cursor: pointer;
  transition: all .15s ease;
}
.zoom-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}
.zoom-btn .material-symbols-outlined {
  font-size: 18px;
}

.zoom-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  min-width: 80px;
  text-align: center;
}

.gantt-container {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 8px 0;
}

.gantt-bar-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 0 4px;
}

.bar-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}

.empty-state {
  text-align: center;
  color: #9ca3af;
  padding: 40px 16px;
  font-size: 14px;
}

/* Tooltip */
.gantt-tooltip {
  position: fixed;
  z-index: 9999;
  background: #1f2937;
  color: #f9fafb;
  padding: 10px 14px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
  pointer-events: none;
  max-width: 320px;
  animation: fadeIn .12s ease-out;
}

.tooltip-title {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 4px;
  line-height: 1.3;
}

.tooltip-dates {
  font-size: 11px;
  color: #d1d5db;
  margin-bottom: 2px;
}

.tooltip-status {
  font-size: 11px;
  font-weight: 600;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>