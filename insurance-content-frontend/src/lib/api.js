import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: window.location.hostname === 'localhost' 
    ? 'http://localhost:5001/api' 
    : '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth headers
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (profileData) => api.put('/auth/update-profile', profileData),
};

// Content API calls
export const contentAPI = {
  generateSchedule: (scheduleData) => api.post('/content/generate-schedule', scheduleData),
  getSchedules: () => api.get('/content/schedules'),
  getSchedule: (scheduleId) => api.get(`/content/schedules/${scheduleId}`),
  deleteSchedule: (scheduleId) => api.delete(`/content/schedules/${scheduleId}`),
  getCurrentWeekSchedule: () => api.get('/content/current-week'),
  getInsuranceTypes: () => api.get('/content/insurance-types'),
  getTones: () => api.get('/content/tones'),
};

// Images API calls
export const imagesAPI = {
  generateImage: (postId) => api.post(`/images/generate-image/${postId}`),
  generateAllImages: (scheduleId) => api.post(`/images/generate-all-images/${scheduleId}`),
  regenerateImage: (postId, imageData) => api.post(`/images/regenerate-image/${postId}`, imageData),
  downloadImage: (postId) => api.get(`/images/download-image/${postId}`),
};

// Subscription API calls
export const subscriptionAPI = {
  createCheckoutSession: (planData) => api.post('/subscription/create-checkout-session', planData),
  getStatus: () => api.get('/subscription/status'),
  getPricing: () => api.get('/subscription/pricing'),
  createPortalSession: () => api.post('/subscription/portal'),
  cancelSubscription: () => api.post('/subscription/cancel-subscription'),
  reactivateSubscription: () => api.post('/subscription/reactivate-subscription'),
};

export default api;
