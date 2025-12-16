import {
  AnalysisRequest,
  AnalysisResponse,
  CompleteAnalysisResults,
  SessionStatus,
} from '../types/api';

class ApiClient {
  private baseUrl: string;

  constructor() {
    // Smart backend URL detection with fallback
    const currentHost = window.location.hostname;

    // Check for environment variable first
    if (import.meta.env.VITE_BACKEND_URL) {
      this.baseUrl = import.meta.env.VITE_BACKEND_URL;
    } else if (currentHost.includes('ngrok') || currentHost.includes('localtunnel') || currentHost.includes('lhr.life')) {
      // 🚀 Tunneling Mode: Use relative path /api to leverage Vite Proxy
      // This allows sharing via a single tunnel (Port 3000) without exposing backend (Port 8000) separately
      this.baseUrl = '/api';
      console.log('🚇 Tunnel detection: Using proxy /api');
    } else if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
      // Local development
      this.baseUrl = 'http://localhost:8000';
    } else {
      // Network access (LAN) - use the same IP as frontend but port 8000
      this.baseUrl = `http://${currentHost}:8000`;
    }

    console.log('🔧 API Base URL:', this.baseUrl);
    console.log('🌐 Frontend Host:', currentHost);
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      mode: 'cors',
      ...options,
    };

    try {
      console.log(`🌐 Making request to: ${url}`);
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error: ${response.status} - ${errorText}`);
        throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log(`✅ API Response:`, data);
        return data;
      } else {
        return response as unknown as T;
      }
    } catch (error) {
      console.error(`❌ API Request failed:`, error);
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        throw new Error(`❌ Cannot connect to backend at ${this.baseUrl}\n\nMake sure:\n1. Backend server is running on port 8000\n2. No firewall is blocking the connection\n3. Backend is accessible from this network`);
      }
      throw new Error(error instanceof Error ? error.message : 'Network request failed');
    }
  }

  async startAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    console.log(`🚀 Starting analysis for: ${request.url}`);
    return this.request<AnalysisResponse>('/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getAnalysisStatus(sessionId: string): Promise<SessionStatus> {
    return this.request<SessionStatus>(`/status/${sessionId}`);
  }

  async getAnalysisResults(sessionId: string): Promise<CompleteAnalysisResults> {
    console.log(`📊 Fetching results for session: ${sessionId}`);
    return this.request<CompleteAnalysisResults>(`/results/${sessionId}`);
  }

  getDownloadUrl(sessionId: string): string {
    return `${this.baseUrl}/download/${sessionId}`;
  }

  async downloadReport(sessionId: string): Promise<void> {
    try {
      const url = this.getDownloadUrl(sessionId);
      console.log(`📥 Downloading report from: ${url}`);

      // Create a temporary link to trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `website_analysis_${sessionId}.txt`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log(`✅ Download triggered for session: ${sessionId}`);
    } catch (error) {
      console.error(`❌ Download failed:`, error);
      throw error;
    }
  }

  getWebSocketUrl(sessionId: string): string {
    const currentHost = window.location.hostname;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

    let wsUrl: string;

    if (currentHost.includes('ngrok') || currentHost.includes('localtunnel') || this.baseUrl === '/api') {
      // 🚇 Tunnel Mode: Use relative path through proxy (requires WS proxying support or direct same-origin)
      // Note: We use window.location.host (includes port if any) to match the current tunnel URL
      wsUrl = `${wsProtocol}${window.location.host}/api/ws/${sessionId}`;
    } else if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
      wsUrl = `${wsProtocol}localhost:8000/ws/${sessionId}`;
    } else {
      wsUrl = `${wsProtocol}${currentHost}:8000/ws/${sessionId}`;
    }

    console.log('🔌 WebSocket URL:', wsUrl);
    return wsUrl;
  }

  getScreenshotUrl(screenshotPath: string): string {
    return `${this.baseUrl}/static/${screenshotPath}`;
  }

  // Health check method
  async checkHealth(): Promise<boolean> {
    try {
      await this.request('/');
      return true;
    } catch (error) {
      console.error('❌ Backend health check failed:', error);
      return false;
    }
  }

  async getImprovementGuide(category: string, context: any): Promise<string> {
    const data = await this.request<{ guide: string }>('/guide', {
      method: 'POST',
      body: JSON.stringify({ category, context }),
    });
    return data.guide;
  }
}

// URL validation utilities
export const validateUrl = (url: string): { isValid: boolean; error?: string } => {
  if (!url || url.trim().length === 0) {
    return { isValid: false, error: 'URL is required' };
  }

  const trimmedUrl = url.trim();

  // Check for obviously invalid formats
  if (trimmedUrl.includes(' ')) {
    return { isValid: false, error: 'URL cannot contain spaces' };
  }

  const urlWithProtocol = trimmedUrl.match(/^https?:\/\//)
    ? trimmedUrl
    : `https://${trimmedUrl}`;

  try {
    const urlObj = new URL(urlWithProtocol);

    // Basic validation
    if (!urlObj.hostname || urlObj.hostname.length < 3) {
      return { isValid: false, error: 'Please enter a valid domain name' };
    }

    // Check for localhost/IP addresses in production
    if (urlObj.hostname === 'localhost' ||
      urlObj.hostname === '127.0.0.1' ||
      urlObj.hostname.match(/^192\.168\./)) {
      return { isValid: false, error: 'Cannot analyze local/private IP addresses' };
    }

    return { isValid: true };
  } catch {
    return { isValid: false, error: 'Please enter a valid URL (e.g., example.com or https://example.com)' };
  }
};

export const normalizeUrl = (url: string): string => {
  if (!url) return '';

  const trimmedUrl = url.trim();
  if (!trimmedUrl.match(/^https?:\/\//)) {
    return `https://${trimmedUrl}`;
  }
  return trimmedUrl;
};

export const formatUrl = (url: string): string => {
  if (!url) return '';
  try {
    const urlObj = new URL(url);
    return urlObj.hostname + (urlObj.pathname !== '/' ? urlObj.pathname : '');
  } catch {
    return url;
  }
};

// Create and export the API client instance
export const apiClient = new ApiClient();

// Export default for easier importing
export default apiClient;