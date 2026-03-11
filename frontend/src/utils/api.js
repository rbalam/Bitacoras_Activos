import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Assets
export const getAssets = (params) => axios.get(`${API}/assets`, { params });
export const getAsset = (id) => axios.get(`${API}/assets/${id}`);
export const createAsset = (data) => axios.post(`${API}/assets`, data);
export const updateAsset = (id, data) => axios.put(`${API}/assets/${id}`, data);

// Maintenances
export const getMaintenances = (params) => axios.get(`${API}/maintenances`, { params });
export const createMaintenance = (data) => axios.post(`${API}/maintenances`, data);
export const updateMaintenance = (id, data) => axios.put(`${API}/maintenances/${id}`, data);

// Maintenance Plans
export const getMaintenancePlans = (params) => axios.get(`${API}/maintenance-plans`, { params });
export const getMaintenancePlan = (id) => axios.get(`${API}/maintenance-plans/${id}`);
export const createMaintenancePlan = (data) => axios.post(`${API}/maintenance-plans`, data);
export const updateMaintenancePlan = (id, data) => axios.put(`${API}/maintenance-plans/${id}`, data);
export const deleteMaintenancePlan = (id) => axios.delete(`${API}/maintenance-plans/${id}`);

// Quotes
export const getQuotes = (params) => axios.get(`${API}/quotes`, { params });
export const createQuote = (data) => axios.post(`${API}/quotes`, data);

// Authorizations
export const getAuthorizations = (params) => axios.get(`${API}/authorizations`, { params });
export const createAuthorization = (data) => axios.post(`${API}/authorizations`, data);
export const approveAuthorization = (id, comentarios, notificar_whatsapp = false) => 
  axios.put(`${API}/authorizations/${id}/approve`, null, { params: { comentarios, notificar_whatsapp } });
export const rejectAuthorization = (id, comentarios, notificar_whatsapp = false) => 
  axios.put(`${API}/authorizations/${id}/reject`, null, { params: { comentarios, notificar_whatsapp } });

// Alerts
export const getAlerts = (params) => axios.get(`${API}/alerts`, { params });
export const markAlertRead = (id) => axios.put(`${API}/alerts/${id}/mark-read`);

// Files
export const uploadFile = (formData) => axios.post(`${API}/upload`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const getFiles = (entityType, entityId) => 
  axios.get(`${API}/files/${entityType}/${entityId}`);
export const downloadFile = (fileId) => 
  `${API}/download/${fileId}`;

// Analytics
export const getDashboardStats = () => axios.get(`${API}/analytics/dashboard`);
export const getAssetCosts = (id) => axios.get(`${API}/analytics/asset/${id}/costs`);
export const checkAssetReplacement = (id) => axios.get(`${API}/analytics/asset/${id}/replacement-check`);


// Reports
export const getMaintenanceHistory = (params) => 
  axios.get(`${API}/reports/maintenance-history`, { params });
export const getAssetSummary = (id) => 
  axios.get(`${API}/reports/asset-summary/${id}`);


// External
export const getExternalInvoices = (serverIndex) => 
  axios.get(`${API}/external/invoices/${serverIndex}`);
export const searchExternalInvoice = (invoiceNumber) => 
  axios.get(`${API}/external/search-invoice/${invoiceNumber}`);
