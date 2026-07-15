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
          </div>

          <div class="flex border border-red-500 rounded-lg overflow-hidden">
            <button 
              @click="currentView = 'Kanban'" 
              :class="{'bg-red-500 text-white': currentView === 'Kanban'}" 
              class="px-4 py-2 hover:bg-red-50">
              Kanban
            </button>
            <button 
              @click="currentView = 'Gantt'" 
              :class="{'bg-red-500 text-white': currentView === 'Gantt'}" 
              class="px-4 py-2 hover:bg-red-50">
              Gantt
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
  <div v-else key="empty-fallback-layout" class="text-gray-400 text-center py-8">
    Sélectionnez une vue pour afficher les tâches du projet.
  </div>
</div>
        
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
import { shallowRef, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

interface Project {
    id: number;
    nom: string;
}

const tasks = ref([]);
const projects = ref<Project[]>([]);
const employees = ref([]);
const currentView = shallowRef('Table');
const selectedProject = ref<string | null>(null);

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

    let start = data.start_date || data.date_debut;
    let due = data.due_date || data.date_fin;

    if (start) {
      cleanData.start_date = typeof start === 'string' ? start.split(' ')[0] : start;
    }

    if (due) {
      cleanData.due_date = typeof due === 'string' ? due.split(' ')[0] : due;
    }

    const activeProject = projects.value.find(p => p.nom === selectedProject.value);
    const projectId = activeProject ? activeProject.id : route.params.id;

    if (!projectId) return;

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
        
        const empResponse = await employeeService.getAllEmployees();
        employees.value = empResponse.data || [];
    } catch(error) {
        console.error("Erreur de chargement des données initiales de la vue :", error);
    }
});
</script>