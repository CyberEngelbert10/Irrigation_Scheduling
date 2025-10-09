import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

// Create axios instance
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add access token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = Cookies.get('access_token');
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // If 401 and we haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        Cookies.set('access_token', access);

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Field Management API
export const fieldAPI = {
  // List all user's fields
  async list(params?: {
    is_active?: boolean;
    crop_type?: string;
    region?: string;
    search?: string;
  }) {
    const response = await api.get('/fields/', { params });
    return response.data;
  },

  // Get field by ID
  async get(id: number) {
    const response = await api.get(`/fields/${id}/`);
    return response.data;
  },

  // Create new field
  async create(data: any) {
    const response = await api.post('/fields/', data);
    return response.data;
  },

  // Update field (partial)
  async update(id: number, data: any) {
    const response = await api.patch(`/fields/${id}/`, data);
    return response.data;
  },

  // Delete field
  async delete(id: number) {
    await api.delete(`/fields/${id}/`);
  },

  // Update soil moisture only
  async updateMoisture(id: number, moisture: number) {
    const response = await api.patch(`/fields/${id}/update-moisture/`, {
      current_soil_moisture: moisture,
    });
    return response.data;
  },

  // Get field statistics
  async getStatistics() {
    const response = await api.get('/fields/statistics/');
    return response.data;
  },

  // Get AI model input
  async getAIInput(id: number, weatherData: {
    temperature: number;
    humidity: number;
    rainfall: number;
    windspeed: number;
  }) {
    const response = await api.get(`/fields/${id}/ai-input/`, {
      params: weatherData,
    });
    return response.data;
  },
};

// Weather API
export const weatherAPI = {
  // Get current weather
  async getCurrent(data: { latitude: number; longitude: number; location_name?: string }) {
    const response = await api.post('/weather/weather-data/current/', data);
    return response.data;
  },

  // Get weather forecast
  async getForecast(data: { latitude: number; longitude: number; days?: number }) {
    const response = await api.post('/weather/forecast/forecast/', data);
    return response.data;
  },

  // Get weather alerts
  async getAlerts(latitude: number, longitude: number) {
    const response = await api.get('/weather/alerts/alerts/', {
      params: { latitude, longitude }
    });
    return response.data;
  },

  // Get weather statistics
  async getStats(latitude: number, longitude: number, days: number = 7) {
    const response = await api.get('/weather/stats/', {
      params: { latitude, longitude, days }
    });
    return response.data;
  },

  // Refresh weather data
  async refresh(data: { latitude: number; longitude: number }) {
    const response = await api.post('/weather/refresh/', data);
    return response.data;
  },
};

// Predictions API
export const predictionsAPI = {
  // Generate irrigation schedule for a field
  async generateSchedule(fieldId: number) {
    const response = await api.post('/predictions/schedules/generate/', {
      field_id: fieldId,
    });
    return response.data;
  },

  // Get all irrigation schedules
  async getSchedules(params?: {
    status?: string;
    field?: number;
    limit?: number;
    offset?: number;
  }) {
    const response = await api.get('/predictions/schedules/', { params });
    return response.data;
  },

  // Get pending schedules
  async getPendingSchedules() {
    const response = await api.get('/predictions/schedules/pending/');
    return response.data;
  },

  // Get overdue schedules
  async getOverdueSchedules() {
    const response = await api.get('/predictions/schedules/overdue/');
    return response.data;
  },

  // Get schedule by ID
  async getSchedule(id: number) {
    const response = await api.get(`/predictions/schedules/${id}/`);
    return response.data;
  },

  // Update schedule status
  async updateSchedule(id: number, data: { status: string }) {
    const response = await api.patch(`/predictions/schedules/${id}/`, data);
    return response.data;
  },

  // Confirm schedule
  async confirmSchedule(id: number) {
    const response = await api.post(`/predictions/schedules/${id}/confirm/`);
    return response.data;
  },

  // Skip schedule
  async skipSchedule(id: number) {
    const response = await api.post(`/predictions/schedules/${id}/skip/`);
    return response.data;
  },

  // Get predictions for all user's fields
  async getFieldPredictions() {
    const response = await api.get('/predictions/predict/field_predictions/');
    return response.data;
  },

  // Get prediction for specific field
  async getFieldPrediction(fieldId: number) {
    const response = await api.post('/predictions/predict/predict/', {
      field_id: fieldId,
    });
    return response.data;
  },

  // Get irrigation history
  async getHistory(params?: {
    field_id?: number;
    limit?: number;
    offset?: number;
  }) {
    const response = await api.get('/predictions/history/', { params });
    return response.data;
  },

  // Get recent history (last 30 days)
  async getRecentHistory() {
    const response = await api.get('/predictions/history/recent/');
    return response.data;
  },

  // Create irrigation history record
  async createHistory(data: any) {
    const response = await api.post('/predictions/history/', data);
    return response.data;
  },

  // Get history by ID
  async getHistoryById(id: number) {
    const response = await api.get(`/predictions/history/${id}/`);
    return response.data;
  },

  // Update history record
  async updateHistory(id: number, data: any) {
    const response = await api.patch(`/predictions/history/${id}/`, data);
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  // Get water usage statistics
  async getWaterUsageStats(params?: { days?: number }) {
    const response = await api.get('/analytics/stats/', { params });
    return response.data;
  },

  // Get field-specific analytics
  async getFieldAnalytics(fieldId: number, params?: { days?: number }) {
    const response = await api.get(`/analytics/field/${fieldId}/`, { params });
    return response.data;
  },

  // Get irrigation efficiency report
  async getEfficiencyReport(params?: { days?: number }) {
    const response = await api.get('/analytics/efficiency/', { params });
    return response.data;
  },
};

// Settings API
export const settingsAPI = {
  // Get user preferences
  async getPreferences() {
    const response = await api.get('/settings/preferences/');
    return response.data;
  },

  // Update user preferences
  async updatePreferences(data: any) {
    const response = await api.patch('/settings/preferences/', data);
    return response.data;
  },

  // Reset preferences to defaults
  async resetPreferences() {
    const response = await api.post('/settings/preferences/reset/');
    return response.data;
  },
};

// Export the axios instance for direct use
export { api };
