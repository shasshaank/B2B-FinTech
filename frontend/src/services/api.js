import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

// ─── Stage 1: Onboarding ────────────────────────────────────────────────────

export const createEntity = (data) => api.post('/entity', data);

export const getEntity = (entityId) => api.get(`/entity/${entityId}`);

export const createLoanDetails = (entityId, data) => api.post(`/entity/${entityId}/loan`, data);

export const getLoanDetails = (entityId) => api.get(`/entity/${entityId}/loan`);

// ─── Stage 2: Document Ingestion ────────────────────────────────────────────

export const uploadDocument = (entityId, file, category = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (category) formData.append('category', category);
  return api.post(`/entity/${entityId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      return percent;
    },
  });
};

export const getDocuments = (entityId) => api.get(`/entity/${entityId}/documents`);

export const deleteDocument = (docId) => api.delete(`/documents/${docId}`);

// ─── Stage 3: Extraction & Classification ────────────────────────────────────

export const classifyDocument = (docId) => api.post(`/documents/${docId}/classify`);

export const confirmClassification = (docId, data) => api.put(`/documents/${docId}/classify/confirm`, data);

export const extractDocument = (docId) => api.post(`/documents/${docId}/extract`);

export const getExtraction = (docId) => api.get(`/documents/${docId}/extraction`);

export const updateExtraction = (docId, extractedData) =>
  api.put(`/documents/${docId}/extraction`, { extracted_data: extractedData });

export const getSchema = (entityId) => api.get(`/entity/${entityId}/schema`);

export const updateSchema = (entityId, schemaData) =>
  api.put(`/entity/${entityId}/schema`, { schema_data: schemaData });

// ─── Stage 4: Analysis & Reporting ──────────────────────────────────────────

export const runSecondaryResearch = (entityId) => api.post(`/entity/${entityId}/secondary-research`);

export const getSecondaryResearch = (entityId) => api.get(`/entity/${entityId}/secondary-research`);

export const generateRecommendation = (entityId) => api.post(`/entity/${entityId}/recommendation`);

export const getRecommendation = (entityId) => api.get(`/entity/${entityId}/recommendation`);

export const generateSwot = (entityId) => api.post(`/entity/${entityId}/swot`);

export const getSwot = (entityId) => api.get(`/entity/${entityId}/swot`);

export const generateReport = (entityId) => api.post(`/entity/${entityId}/report`);

export const getReport = (entityId) => api.get(`/entity/${entityId}/report`);

export const getReportDownloadUrl = (entityId) =>
  `${API_BASE}/entity/${entityId}/report/download`;

export default api;
