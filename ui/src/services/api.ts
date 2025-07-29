import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add error interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Channel APIs
export const channelAPI = {
  list: (limit = 20, offset = 0) => 
    api.get(`/channels?limit=${limit}&offset=${offset}`),
  create: (data: { name: string; description?: string; max_agents?: number }) =>
    api.post('/channels', data),
  delete: (channelId: string) =>
    api.delete(`/channels/${channelId}`),
};

// Agent APIs
export const agentAPI = {
  list: (channelId: string) => 
    api.get(`/channels/${channelId}/agents`),
};

// Message APIs
export const messageAPI = {
  list: (channelId: string, limit = 50) =>
    api.get(`/channels/${channelId}/messages?limit=${limit}`),
};