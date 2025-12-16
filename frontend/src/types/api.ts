// Request Types
export interface AnalysisRequest {
  url: string;
  options?: Record<string, any>;
}

// Response Types
export interface AnalysisResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface ViewportInfo {
  name: string;
  width: number;
  height: number;
  screenshot_path?: string;
  issues?: DetectedIssue[];
  captured_at?: number;
  error?: string;
}

export interface DetectedIssue {
  id?: number;
  category: 'layout' | 'accessibility' | 'seo' | 'performance' | 'forms';
  issue_type: string;
  severity: 'high' | 'medium' | 'low';
  description: string;
  element_selector?: string;
  viewport?: string;
  ai_suggestion?: string;
  fix_code?: string;
  elements?: any[];
  suggestion?: string;
}

export interface AnalysisScores {
  responsiveness: number;
  accessibility: number;
  seo: number;
  performance: number;
  overall: number;
}

export interface CompleteAnalysisResults {
  session_id: string;
  url: string;
  status: string;
  created_at: string;
  completed_at?: string;
  viewports: ViewportInfo[];
  issues: DetectedIssue[];
  seo: any;
  performance: any;
  platform: any;
  forms: any;
  ai_analysis: any;
  scores: AnalysisScores;
}

export interface SessionStatus {
  session_id: string;
  status: 'started' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  current_step?: string;
  current_viewport?: string;
  updated_at?: string;
  error?: string;
}

export interface WebSocketMessage {
  type: 'connection' | 'progress' | 'completed' | 'error';
  session_id: string;
  message: string;
  progress?: number;
  step?: string;
  viewport?: string;
  data?: any;
  timestamp: string;
}

// Constants
export const SEVERITY_COLORS = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#10b981',
} as const;

export const CATEGORY_COLORS = {
  layout: '#8b5cf6',
  accessibility: '#06b6d4',
  seo: '#84cc16',
  performance: '#f59e0b',
  forms: '#ec4899',
} as const;

export const VIEWPORT_INFO = {
  'Mobile Small': { icon: '📱', description: 'iPhone SE (320×568)' },
  'Mobile Medium': { icon: '📱', description: 'iPhone 8 (375×667)' },
  'Mobile Large': { icon: '📱', description: 'iPhone X (425×812)' },
  'Tablet': { icon: '📟', description: 'iPad (768×1024)' },
  'Tablet Landscape': { icon: '📟', description: 'iPad Landscape (1024×768)' },
  'Desktop': { icon: '💻', description: 'Desktop (1440×900)' },
  'Desktop Large': { icon: '🖥️', description: 'Large Desktop (2560×1440)' },
} as const;