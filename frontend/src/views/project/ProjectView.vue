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
import AppLayout from "@/layouts/AppLayout.vue";
import GanttView from '@/components/project/GanttView.vue';
import KanbanView from '@/components/project/KanbanView.vue';
import {shallowRef, ref, onMounted} from 'vue';

interface Project {
    id: number;
    nom: string;
}
const tasks = ref([]);

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
        tasks.value = []; // Clear tasks if no valid project is selected
    }
};
const handleTaskUpdate = async (taskId: number, data: any) => {
  try {
    const project = projects.value.find(p => p.nom === selectedProject.value);
    if (project) {
      await taskService.updateTask(project.id, taskId, data);
      // Refresh tasks to reflect changes
      await loadTasks();
    }
  } catch (error) {
    console.error('Failed to update task', error);
  }
};

const projects = ref<Project[]>([]);

onMounted(async ()=>{
    try{
        const response = await projectService.getAllProjects();
    projects.value = response.data;
    }catch(error){
        console.error("Erreur de chargement des projets.")
    }
});
const currentView = shallowRef('Table');
const selectedProject = ref<string | null>(null);
</script>