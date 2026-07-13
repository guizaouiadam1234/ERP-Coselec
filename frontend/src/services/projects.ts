import api from './api';

export const projectService = {
  // Gestion des projets globaux
  getAllProjects: () => api.get('/projects/'),
  getProjectById: (projectId: number) => api.get(`/projects/${projectId}`),
  createProject: (data: any) => api.post('/projects/', data),
};

export const taskService = {
  // Gestion des tâches liées à un projet
  getTasksByProject: (projectId: number) => api.get(`/projects/${projectId}/tasks`),
  createTask: (projectId: number, data: any) => api.post(`/projects/${projectId}/tasks/`, data),
  
  // Gestion des tâches globales (déplacement ou modif transversale)
  updateTask: (taskId: number, data: any) => api.patch(`/tasks/${taskId}`, data),
  deleteTask: (taskId: number) => api.delete(`/tasks/${taskId}`)
};