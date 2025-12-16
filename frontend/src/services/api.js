import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Story API
export const storyAPI = {
  // Get all stories
  getStories: () => api.get('/stories'),
  
  // Get a specific story
  getStory: (id) => api.get(`/stories/${id}`),
  
  // Create a new story
  createStory: (data) => api.post('/stories', data),
  
  // Update story
  updateStory: (id, data) => api.put(`/stories/${id}`, data),
  
  // Delete story
  deleteStory: (id) => api.delete(`/stories/${id}`),
  
  // Generate PDDL
  generatePDDL: (id) => api.post(`/stories/${id}/generate-pddl`),
  
  // Validate PDDL
  validatePDDL: (id) => api.post(`/stories/${id}/validate`),
  
  // Refine PDDL
  refinePDDL: (id, data) => api.post(`/stories/${id}/refine`, data),
  
  // Chat with reflection agent
  chatWithAgent: (id, data) => api.post(`/stories/${id}/chat`, data),
  
  // Get refinement history
  getRefinementHistory: (id) => api.get(`/stories/${id}/refinement-history`),
};

// Game API
export const gameAPI = {
  // Create game session
  createSession: (storyId) => api.post('/game/sessions', { story_id: storyId }),
  
  // Get game session
  getSession: (id) => api.get(`/game/sessions/${id}`),
  
  // Take action in game
  takeAction: (id, action) => api.post(`/game/sessions/${id}/action`, { action }),
  
  // Get session history
  getSessionHistory: (id) => api.get(`/game/sessions/${id}/history`),
  
  // List all sessions
  listSessions: (storyId) => api.get('/game/sessions', { params: { story_id: storyId } }),
  
  // Delete session
  deleteSession: (id) => api.delete(`/game/sessions/${id}`),
};

// Health API
export const healthAPI = {
  check: () => api.get('/health'),
  getConfig: () => api.get('/config'),
};

export default api;
