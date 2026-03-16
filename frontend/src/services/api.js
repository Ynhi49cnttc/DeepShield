import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 180000 // 3 minutes for AI processing
});

export const imageAPI = {
  /**
   * Upload an image
   */
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('image', file);

    const response = await axios.post(`${API_BASE_URL}/images/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  /**
   * ==================== NEW AI ENDPOINTS ====================
   */

  /**
   * Protect image with AI
   */
  protectImageWithAI: async (filename, method = 'deepshield') => {
    const response = await api.post('/images/protect-ai', { 
      filename,
      method 
    });
    return response.data;
  },

  /**
   * Compare all methods with AI
   */
  compareMethodsWithAI: async (filename) => {
    const response = await api.post('/images/compare-ai', { 
      filename 
    });
    return response.data;
  },

  /**
   * Complete workflow with AI (RECOMMENDED)
   */
  processCompleteWithAI: async (file, method = 'deepshield') => {
    const formData = new FormData();
    formData.append('image', file);

    const response = await axios.post(
      `${API_BASE_URL}/images/process-complete-ai`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 180000
      }
    );
    return response.data;
  },

  /**
   * Check AI service status
   */
  checkAIStatus: async () => {
    try {
      const response = await api.get('/images/ai-status');
      return response.data;
    } catch (error) {
      return {
        aiServiceAvailable: false,
        error: error.message
      };
    }
  },

  /**
   * ==================== OLD ENDPOINTS (Simulation) ====================
   * Kept for backward compatibility
   */
  
  protectImage: async (filename) => {
    const response = await api.post('/images/protect', { filename });
    return response.data;
  },

  simulateDeepfake: async (filename, isProtected = false) => {
    const response = await api.post('/images/simulate-deepfake', { 
      filename, 
      isProtected 
    });
    return response.data;
  },

  processComplete: async (file) => {
    const formData = new FormData();
    formData.append('image', file);

    const response = await axios.post(`${API_BASE_URL}/images/process-complete`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;