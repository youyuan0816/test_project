import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import type { Task } from '@/services/types';

export function useTasks() {
  const query = useQuery({
    queryKey: ['tasks'],
    queryFn: api.getTasks,
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 0,
  });

  const syncToLocalStore = (tasks: Task[]) => {
    const { addTask, updateTask } = useTaskStore.getState();
    const localTasks = useTaskStore.getState().tasks;

    // Sync: update or add tasks from backend
    tasks.forEach((task) => {
      const existing = localTasks.find((t) => t.id === task.id);
      if (existing) {
        updateTask(task.id, {
          name: task.name,
          status: task.status,
          result: task.result_message,
          result_file: task.result_file,
        });
      } else {
        addTask({
          name: task.name,
          url: task.url,
          description: task.description,
          status: task.status,
          result: task.result_message,
          result_file: task.result_file,
        });
      }
    });
  };

  // Sync tasks to local store when query succeeds
  useEffect(() => {
    if (query.data?.tasks) {
      syncToLocalStore(query.data.tasks);
    }
  }, [query.data?.tasks]);

  return query;
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  const { addTask } = useTaskStore();

  return useMutation({
    mutationFn: async (data: {
      type: 'generate' | 'continue';
      url?: string;
      filepath?: string;
      excel_file?: string;
      description?: string;
      username?: string;
      password?: string;
    }) => {
      if (data.type === 'generate') {
        return api.generate({
          url: data.url!,
          filepath: data.filepath!,
          description: data.description!,
          username: data.username,
          password: data.password,
        });
      } else {
        return api.continueSession({
          excel_file: data.excel_file!,
        });
      }
    },
    onSuccess: (_response, variables) => {
      // Add to local store immediately with pending status
      addTask({
        name: variables.filepath || variables.excel_file || 'Untitled',
        url: variables.url || '',
        description: variables.description || '',
        status: 'pending',
      });
      // Invalidate to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
