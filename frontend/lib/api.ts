import axios, {AxiosInstance, AxiosError} from 'axios';
import { User, AuthResponse, LoginRequest, RegisterRequest, PPTGenerationResponse } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_id');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/register', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/login', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/logout');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/me');
    return response.data;
  },
};

// PPT API functions
export const pptAPI = {
  generate: async (prompt: string): Promise<PPTGenerationResponse> => {
    const response = await apiClient.post<PPTGenerationResponse>('/create-ppt', { prompt });
    return response.data;
  },

  getJobs: async () => {
    const response = await apiClient.get('/jobs');
    return response.data;
  },

  downloadFile: async (filename: string): Promise<Blob> => {
    const response = await apiClient.get(`/download/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
