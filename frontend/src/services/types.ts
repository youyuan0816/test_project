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
