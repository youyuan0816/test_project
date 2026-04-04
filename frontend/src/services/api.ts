import axios from 'axios';
import type { GenerateRequest, ContinueRequest, GenerateResponse, SessionsResponse, Task, TasksResponse } from './types';

const API_BASE = '/api';

export const api = {
  generate: async (data: GenerateRequest): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE}/generate`, data);
    return response.data;
  },

  continueSession: async (data: ContinueRequest): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE}/continue`, data);
    return response.data;
  },

  getSessions: async (): Promise<SessionsResponse> => {
    const response = await axios.get(`${API_BASE}/sessions`);
    return response.data;
  },

  health: async (): Promise<{ status: string }> => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },

  getTasks: async (): Promise<TasksResponse> => {
    const response = await axios.get(`${API_BASE}/tasks`);
    return response.data;
  },

  getTask: async (id: string): Promise<Task> => {
    const response = await axios.get(`${API_BASE}/tasks/${id}`);
    return response.data;
  },
};
