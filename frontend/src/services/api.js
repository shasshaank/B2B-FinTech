/**
 * CreditLens API service layer
 * Handles all communication with the FastAPI backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

// Stage 1: Entity Onboarding
export const entityAPI = {
  create: (data) => api.post('/entity', data),
  get: (id) => api.get(`/entity/${id}`),
  update: (id, data) => api.put(`/entity/${id}`, data),
  createLoan: (entityId, data) => api.post(`/entity/${entityId}/loan`, data),
  getLoans: (entityId) => api.get(`/entity/${entityId}/loan`),
};

// Stage 2: Document Ingestion
export const documentAPI = {
  upload: (entityId, file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    const config = {
      headers: { 'Content-Type': 'multipart/form-data' },
    };
    if (onProgress) {
      config.onUploadProgress = onProgress;
    }
    return api.post(`/entity/${entityId}/documents`, formData, config);
  },
  getAll: (entityId) => api.get(`/entity/${entityId}/documents`),
  delete: (documentId) => api.delete(`/documents/${documentId}`),
};

// Stage 3: Extraction & Classification
export const extractionAPI = {
  classify: (documentId) => api.post(`/documents/${documentId}/classify`),
  classifyAll: (entityId) => api.post(`/entity/${entityId}/classify-all`),
  confirmClassification: (documentId, data) => api.put(`/documents/${documentId}/classify/confirm`, data),
  extract: (documentId) => api.post(`/documents/${documentId}/extract`),
  extractAll: (entityId) => api.post(`/entity/${entityId}/extract-all`),
  getExtraction: (documentId) => api.get(`/documents/${documentId}/extraction`),
  updateExtraction: (documentId, data) => api.put(`/documents/${documentId}/extraction`, { extracted_data: data }),
  getSchema: (entityId) => api.get(`/entity/${entityId}/schema`),
  updateSchema: (entityId, schemas) => api.put(`/entity/${entityId}/schema`, { schemas }),
};

// Stage 4: Analysis & Reporting
export const analysisAPI = {
  runSecondaryResearch: (entityId) => api.post(`/entity/${entityId}/secondary-research`),
  getSecondaryResearch: (entityId) => api.get(`/entity/${entityId}/secondary-research`),
  generateRecommendation: (entityId) => api.post(`/entity/${entityId}/recommendation`),
  getRecommendation: (entityId) => api.get(`/entity/${entityId}/recommendation`),
  generateSwot: (entityId) => api.post(`/entity/${entityId}/swot`),
  getSwot: (entityId) => api.get(`/entity/${entityId}/swot`),
  generateReport: (entityId) => api.post(`/entity/${entityId}/report`),
  getReport: (entityId) => api.get(`/entity/${entityId}/report`),
  downloadReport: (entityId) => `${API_BASE_URL}/entity/${entityId}/report/download`,
};

export default api;
