<template>
  <div class="project-view-root w-full">
    <AppLayout>
      <div class="flex flex-col w-full gap-6 p-4">
        
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center space-x-4">
            <span class="material-symbols-outlined text-[#d10f2f]">work</span>
            <h2 class="text-2xl font-bold text-[#b30c27]">Projet à gérer</h2>
            <select v-model="selectedProject" @change="loadTasks" class="border-2 w-max h-10 rounded-lg px-2">
               <option v-for="p in projects" :key="p.id" :value="p.nom">
                 {{ p.nom }}
               </option>
            </select>
            <button class ="ml-5 bg-[#d10f2f] border-2 border-[#b30c27] rounded-lg w-40 h-10 text-white flex items-center"
            v-if="selectedProject"
            @click="openTaskCreateModal"
            >
              <span class="material-symbols-outlined">add</span>
              <span class="ml-2">Nouvelle tâche</span></button>
          </div>

          <div class="flex border border-red-500 rounded-lg overflow-hidden">
            <button 
              @click="currentView = 'Kanban'" 
              :class="{'bg-red-500 text-white': currentView === 'Kanban', 'text-red-600': currentView !== 'Kanban'}" 
              class="px-4 py-2 hover:bg-red-50 font-medium transition-colors">
              Kanban
            </button>
            <button 
              @click="currentView = 'Gantt'" 
              :class="{'bg-red-500 text-white': currentView === 'Gantt', 'text-red-600': currentView !== 'Gantt'}" 
              class="px-4 py-2 hover:bg-red-50 font-medium transition-colors border-l border-red-500">
              Gantt
            </button>
            <button 
              @click="currentView = 'Ressources'" 
              :class="{'bg-red-500 text-white': currentView === 'Ressources', 'text-red-600': currentView !== 'Ressources'}" 
              class="px-4 py-2 hover:bg-red-50 font-medium transition-colors border-l border-red-500">
              Ressources
            </button>
          </div>
        </div>

       
        <div class="relative w-full min-h-75">
  <GanttView 
    v-if="currentView === 'Gantt'" 
    key="gantt-chart-layout" 
    :tasks="tasks" 
    @update-task="handleTaskUpdate" 
  />
  <KanbanView 
  v-else-if="currentView === 'Kanban'" 
  key="kanban-board-layout" 
  :tasks="tasks" 
  :employees-list="employees"
  @update-task="handleTaskUpdate"
  />
  <ProjectResources
    v-else-if="currentView === 'Ressources'"
    key="resources-layout"
    :project-id="resolveActiveProjectId()"
  />
  <div v-else key="empty-fallback-layout" class="text-gray-400 text-center py-8">
    Sélectionnez une vue pour afficher les données du projet.
  </div>
  </div>
    <TaskCreateModal
      v-if="isTaskCreateModalOpen"
      :open="isTaskCreateModalOpen"
      :employees="employees"
      @close="closeTaskCreateModal"
      @create="handleTaskCreate"
    />
      </div>
    </AppLayout>
  </div>
</template>
<script setup lang="ts">
import { projectService, taskService } from '@/services/projects';
import { employeeService } from '@/services/employees';
import AppLayout from "@/layouts/AppLayout.vue";
import GanttView from '@/components/project/GanttView.vue';
import KanbanView from '@/components/project/KanbanView.vue';
import ProjectResources from '@/components/project/ProjectResources.vue';
import { shallowRef, ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import TaskCreateModal from "@/components/project/TaskCreateModal.vue";
const route = useRoute();

interface Project {
    id: number;
    nom: string;
}

const tasks = ref([]);
const projects = ref<Project[]>([]);
const employees = ref([]);
const currentView = shallowRef('Kanban');
const selectedProject = ref<string | null>(null);
const isTaskCreateModalOpen = ref(false);


const openTaskCreateModal = () => {
  isTaskCreateModalOpen.value = true;
};

const closeTaskCreateModal = () => {
  isTaskCreateModalOpen.value = false;
};

const resolveActiveProjectId = (): number | null => {
  const activeProject = projects.value.find((p) => p.nom === selectedProject.value);

  if (activeProject?.id) {
    return Number(activeProject.id);
  }

  const routeId = Number(route.params.id);
  return Number.isFinite(routeId) && routeId > 0 ? routeId : null;
};

const handleTaskCreate = async (rawData: any) => {
  try {
    const projectId = resolveActiveProjectId();
    if (!projectId) {
      console.error('Aucun projet actif pour creer la tache');
      return;
    }

    const data = rawData?.payload ?? {};
    const files: File[] = Array.isArray(rawData?.files) ? rawData.files : [];

    const response = await taskService.createTask(projectId, data);
    const taskId = response?.data?.id;

    if (taskId && files.length > 0) {
      await taskService.uploadTaskDocuments(projectId, Number(taskId), files);
    }

    isTaskCreateModalOpen.value = false;
    await loadTasks();
  } catch (error: any) {
    console.error('Erreur lors de la creation de la tache', error);
  }
};


const loadTasks = async () => {
  const project = projects.value.find(p => p.nom === selectedProject.value);
  if (project) {
        try {
            const response = await taskService.getTasksByProject(project.id);
            tasks.value = response.data || [];
        } catch (error) {
            console.error("Erreur de chargement des tâches", error);
            tasks.value = [];
        }
    } else {
        tasks.value = [];
    }
};

const toIsoDateOnly = (value: unknown): string | null => {
  if (!value) return null;

  if (typeof value === 'string') {
    // Accept values like "YYYY-MM-DD 00:00" and keep only the date part.
    const trimmed = value.trim();
    if (/^\d{4}-\d{2}-\d{2}/.test(trimmed)) {
      return trimmed.slice(0, 10);
    }

    // Accept values like DD/MM/YYYY from localized pickers.
    const ddmmyyyy = trimmed.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    if (ddmmyyyy) {
      const [, dd, mm, yyyy] = ddmmyyyy;
      return `${yyyy}-${mm}-${dd}`;
    }

    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString().slice(0, 10);
    }

    return null;
  }

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value.toISOString().slice(0, 10);
  }

  // Dayjs-like objects returned by gantt libs.
  if (typeof value === 'object' && value !== null) {
    const maybeAny = value as any;

    if (typeof maybeAny.format === 'function') {
      const formatted = maybeAny.format('YYYY-MM-DD');
      if (typeof formatted === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(formatted)) {
        return formatted;
      }
    }

    if (typeof maybeAny.toDate === 'function') {
      const asDate = maybeAny.toDate();
      if (asDate instanceof Date && !Number.isNaN(asDate.getTime())) {
        return asDate.toISOString().slice(0, 10);
      }
    }

    if (maybeAny.$d instanceof Date && !Number.isNaN(maybeAny.$d.getTime())) {
      return maybeAny.$d.toISOString().slice(0, 10);
    }
  }

  return null;
};

const handleTaskUpdate = async (taskId: number, rawData: any) => {
  try {
    if (!rawData) return;

    const data = rawData.payload ?? rawData;
    const files: File[] = Array.isArray(rawData.files) ? rawData.files : [];

    const cleanData: any = {};
    
    if (data.title) cleanData.title = data.title;
    if (data.status) cleanData.status = data.status;
    if (data.priority) cleanData.priority = data.priority;
    if (data.description) cleanData.description = data.description;
    
    if (data.assignee_id !== undefined) {
      cleanData.assignee_id = data.assignee_id || null;
    }
    
    if (data.project_id !== undefined) {
      cleanData.project_id = data.project_id;
    }

    const start = data.start_date || data.date_debut;
    const due = data.due_date || data.date_fin;

    const normalizedStart = toIsoDateOnly(start);
    const normalizedDue = toIsoDateOnly(due);

    if (normalizedStart) {
      cleanData.start_date = normalizedStart;
    }

    if (normalizedDue) {
      cleanData.due_date = normalizedDue;
    }

    const activeProject = projects.value.find(p => p.nom === selectedProject.value);
    const projectId = activeProject ? activeProject.id : route.params.id;

    if (!projectId) return;

    if (Object.keys(cleanData).length === 0) {
      return;
    }

    await taskService.updateTask(Number(projectId), taskId, cleanData);

    if (files.length > 0) {
      await taskService.uploadTaskDocuments(Number(projectId), taskId, files);
    }

    await loadTasks();
    
  } catch (error: any) {
    console.error("Failed to update task", error);
  }
};

onMounted(async () => {
    try {
        const projectResponse = await projectService.getAllProjects();
        projects.value = projectResponse.data;
        
        if (projects.value.length > 0 && !selectedProject.value) {
            selectedProject.value = projects.value[0]?.nom || null;
            await loadTasks();
        }
        
        const empResponse = await employeeService.getAllEmployees();
        employees.value = empResponse.data || [];
    } catch(error) {
        console.error("Erreur de chargement des données initiales de la vue :", error);
    }
});
</script>