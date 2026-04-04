import { create } from 'zustand';

export interface Task {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  result?: string;
  result_file?: string;
}

interface TaskStore {
  tasks: Task[];
  addTask: (task: Omit<Task, 'id' | 'createdAt'> & { id?: string }) => string;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;
  clearTasks: () => void;
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],

  addTask: (task) => {
    const id = task.id || `task-${Date.now()}`;
    const newTask: Task = {
      ...task,
      id,
      createdAt: new Date().toISOString(),
    };
    set((state) => ({ tasks: [...state.tasks, newTask] }));
    return id;
  },

  updateTask: (id, updates) => {
    set((state) => ({
      tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...updates } : t)),
    }));
  },

  removeTask: (id) => {
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== id),
    }));
  },

  clearTasks: () => {
    set({ tasks: [] });
  },
}));
