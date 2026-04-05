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
  task_id?: string;
}

export interface Session {
  id: string;
  task_id: string;
  excel_path: string;
  title?: string;
  time_created?: number;
  time_updated?: number;
  last_used: string;
  status: string;
  created_at: string;
  deleted_at?: string;
}

export interface GenerateResponse {
  status: 'success' | 'warning' | 'error';
  message: string;
  output?: string;
}

export interface SessionsResponse {
  sessions: Session[];
}

// Task types
export interface Task {
  id: string;
  name: string;
  task_type: 'generate_excel' | 'generate_code';
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  phase?: 'excel_generation' | 'code_generation';
  session_id?: string;
  result_file?: string;
  result_message?: string;
  created_at: string;
  completed_at?: string;
  deleted_at?: string;
}

export interface TasksResponse {
  tasks: Task[];
}

export interface CreateTaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TestCase {
  task_id: string;
  name: string;
  excel_file?: string;
  test_code_dir?: string;
  created_at: string;
}

export interface TestCasesResponse {
  testcases: TestCase[];
}
