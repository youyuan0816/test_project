export interface GenerateRequest {
  url: string;
  filepath: string;
  username?: string;
  password?: string;
  description: string;
  continue_excel?: string;
}

export interface ContinueRequest {
  excel_file: string;
}

export interface Session {
  session_id: string;
  created_at: string;
  last_used: string;
}

export interface GenerateResponse {
  status: 'success' | 'warning' | 'error';
  message: string;
  output?: string;
}

export interface SessionsResponse {
  status: 'success';
  sessions: Record<string, Session>;
}

// Task types
export interface Task {
  id: string;
  name: string;
  task_type: 'generate_excel' | 'generate_code';
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  session_id?: string;
  result_file?: string;
  result_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface TasksResponse {
  tasks: Task[];
}

export interface CreateTaskResponse {
  task_id: string;
  status: string;
  message: string;
}
