import api from "./axios";

export const getTasks = (projectId) => api.get(`/projects/${projectId}/tasks`);
export const createTask = (projectId, data) => api.post(`/projects/${projectId}/tasks`, data);
export const updateTask = (taskId, data) => api.put(`/tasks/${taskId}`, data);
export const deleteTask = (taskId) => api.delete(`/tasks/${taskId}`);
export const getTaskLogs = (taskId) => api.get(`/tasks/${taskId}/logs`);
export const getAnalytics = (projectId) => api.get(`/analytics/projects/${projectId}`);