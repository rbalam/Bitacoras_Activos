import axios from 'axios';
import {
  getAssets,
  getAsset,
  createAsset,
  updateAsset,
  getMaintenances,
  createMaintenance,
  updateMaintenance,
  getMaintenancePlans,
  getMaintenancePlan,
  createMaintenancePlan,
  updateMaintenancePlan,
  deleteMaintenancePlan,
  getQuotes,
  createQuote,
  getAuthorizations,
  createAuthorization,
  approveAuthorization,
  rejectAuthorization,
  getAlerts,
  markAlertRead,
  uploadFile,
  getFiles,
  downloadFile,
  getDashboardStats,
  getAssetCosts,
  checkAssetReplacement,
  getMaintenanceHistory,
  getAssetSummary,
  getExternalInvoices,
  searchExternalInvoice
} from './api';

jest.mock('axios');

describe('API Utils', () => {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Assets', () => {
    it('getAssets calls axios.get with correct url and params', async () => {
      const mockData = { data: [{ id: 1, name: 'Asset 1' }] };
      axios.get.mockResolvedValueOnce(mockData);

      const params = { page: 1 };
      const result = await getAssets(params);

      expect(axios.get).toHaveBeenCalledWith(`${API}/assets`, { params });
      expect(result).toEqual(mockData);
    });

    it('getAsset calls axios.get with correct url', async () => {
      const mockData = { data: { id: 1, name: 'Asset 1' } };
      axios.get.mockResolvedValueOnce(mockData);

      const id = 1;
      const result = await getAsset(id);

      expect(axios.get).toHaveBeenCalledWith(`${API}/assets/${id}`);
      expect(result).toEqual(mockData);
    });

    it('createAsset calls axios.post with correct url and data', async () => {
      const mockData = { data: { id: 1, name: 'New Asset' } };
      axios.post.mockResolvedValueOnce(mockData);

      const data = { name: 'New Asset' };
      const result = await createAsset(data);

      expect(axios.post).toHaveBeenCalledWith(`${API}/assets`, data);
      expect(result).toEqual(mockData);
    });

    it('updateAsset calls axios.put with correct url and data', async () => {
      const mockData = { data: { id: 1, name: 'Updated Asset' } };
      axios.put.mockResolvedValueOnce(mockData);

      const id = 1;
      const data = { name: 'Updated Asset' };
      const result = await updateAsset(id, data);

      expect(axios.put).toHaveBeenCalledWith(`${API}/assets/${id}`, data);
      expect(result).toEqual(mockData);
    });
  });

  describe('Maintenances', () => {
    it('getMaintenances calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { status: 'pending' };
      const result = await getMaintenances(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenances`, { params });
      expect(result).toEqual(mockData);
    });

    it('createMaintenance calls axios.post with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.post.mockResolvedValueOnce(mockData);
      const data = { description: 'Fix' };
      const result = await createMaintenance(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/maintenances`, data);
      expect(result).toEqual(mockData);
    });

    it('updateMaintenance calls axios.put with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const data = { description: 'Fix' };
      const result = await updateMaintenance(id, data);
      expect(axios.put).toHaveBeenCalledWith(`${API}/maintenances/${id}`, data);
      expect(result).toEqual(mockData);
    });
  });

  describe('Maintenance Plans', () => {
    it('getMaintenancePlans calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { active: true };
      const result = await getMaintenancePlans(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenance-plans`, { params });
      expect(result).toEqual(mockData);
    });

    it('getMaintenancePlan calls axios.get with correct url', async () => {
      const mockData = { data: { id: 1 } };
      axios.get.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await getMaintenancePlan(id);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenance-plans/${id}`);
      expect(result).toEqual(mockData);
    });

    it('createMaintenancePlan calls axios.post with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.post.mockResolvedValueOnce(mockData);
      const data = { name: 'Plan 1' };
      const result = await createMaintenancePlan(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/maintenance-plans`, data);
      expect(result).toEqual(mockData);
    });

    it('updateMaintenancePlan calls axios.put with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const data = { name: 'Plan 1' };
      const result = await updateMaintenancePlan(id, data);
      expect(axios.put).toHaveBeenCalledWith(`${API}/maintenance-plans/${id}`, data);
      expect(result).toEqual(mockData);
    });

    it('deleteMaintenancePlan calls axios.delete with correct url', async () => {
      const mockData = { data: { success: true } };
      axios.delete.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await deleteMaintenancePlan(id);
      expect(axios.delete).toHaveBeenCalledWith(`${API}/maintenance-plans/${id}`);
      expect(result).toEqual(mockData);
    });
  });

  describe('Quotes', () => {
    it('getQuotes calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { limit: 10 };
      const result = await getQuotes(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/quotes`, { params });
      expect(result).toEqual(mockData);
    });

    it('createQuote calls axios.post with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.post.mockResolvedValueOnce(mockData);
      const data = { amount: 100 };
      const result = await createQuote(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/quotes`, data);
      expect(result).toEqual(mockData);
    });
  });

  describe('Authorizations', () => {
    it('getAuthorizations calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { status: 'pending' };
      const result = await getAuthorizations(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/authorizations`, { params });
      expect(result).toEqual(mockData);
    });

    it('createAuthorization calls axios.post with correct url and data', async () => {
      const mockData = { data: { id: 1 } };
      axios.post.mockResolvedValueOnce(mockData);
      const data = { userId: 1 };
      const result = await createAuthorization(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/authorizations`, data);
      expect(result).toEqual(mockData);
    });

    it('approveAuthorization calls axios.put with correct url and params', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const comentarios = 'OK';
      const notificar_whatsapp = true;
      const result = await approveAuthorization(id, comentarios, notificar_whatsapp);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/${id}/approve`, null, { params: { comentarios, notificar_whatsapp } });
      expect(result).toEqual(mockData);
    });

    it('approveAuthorization calls axios.put with default notificar_whatsapp', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const comentarios = 'OK';
      const result = await approveAuthorization(id, comentarios);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/${id}/approve`, null, { params: { comentarios, notificar_whatsapp: false } });
      expect(result).toEqual(mockData);
    });

    it('rejectAuthorization calls axios.put with correct url and params', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const comentarios = 'NO';
      const notificar_whatsapp = true;
      const result = await rejectAuthorization(id, comentarios, notificar_whatsapp);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/${id}/reject`, null, { params: { comentarios, notificar_whatsapp } });
      expect(result).toEqual(mockData);
    });

    it('rejectAuthorization calls axios.put with default notificar_whatsapp', async () => {
      const mockData = { data: { id: 1 } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const comentarios = 'NO';
      const result = await rejectAuthorization(id, comentarios);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/${id}/reject`, null, { params: { comentarios, notificar_whatsapp: false } });
      expect(result).toEqual(mockData);
    });
  });

  describe('Alerts', () => {
    it('getAlerts calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { unread: true };
      const result = await getAlerts(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/alerts`, { params });
      expect(result).toEqual(mockData);
    });

    it('markAlertRead calls axios.put with correct url', async () => {
      const mockData = { data: { success: true } };
      axios.put.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await markAlertRead(id);
      expect(axios.put).toHaveBeenCalledWith(`${API}/alerts/${id}/mark-read`);
      expect(result).toEqual(mockData);
    });
  });

  describe('Files', () => {
    it('uploadFile calls axios.post with correct url, data, and headers', async () => {
      const mockData = { data: { success: true } };
      axios.post.mockResolvedValueOnce(mockData);
      const formData = new FormData();
      const result = await uploadFile(formData);
      expect(axios.post).toHaveBeenCalledWith(`${API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      expect(result).toEqual(mockData);
    });

    it('getFiles calls axios.get with correct url', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const entityType = 'asset';
      const entityId = 1;
      const result = await getFiles(entityType, entityId);
      expect(axios.get).toHaveBeenCalledWith(`${API}/files/${entityType}/${entityId}`);
      expect(result).toEqual(mockData);
    });

    it('downloadFile returns correct url string', () => {
      const fileId = 123;
      const result = downloadFile(fileId);
      expect(result).toBe(`${API}/download/${fileId}`);
    });
  });

  describe('Analytics', () => {
    it('getDashboardStats calls axios.get with correct url', async () => {
      const mockData = { data: {} };
      axios.get.mockResolvedValueOnce(mockData);
      const result = await getDashboardStats();
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/dashboard`);
      expect(result).toEqual(mockData);
    });

    it('getAssetCosts calls axios.get with correct url', async () => {
      const mockData = { data: {} };
      axios.get.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await getAssetCosts(id);
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/${id}/costs`);
      expect(result).toEqual(mockData);
    });

    it('checkAssetReplacement calls axios.get with correct url', async () => {
      const mockData = { data: {} };
      axios.get.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await checkAssetReplacement(id);
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/${id}/replacement-check`);
      expect(result).toEqual(mockData);
    });
  });

  describe('Reports', () => {
    it('getMaintenanceHistory calls axios.get with correct url and params', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const params = { assetId: 1 };
      const result = await getMaintenanceHistory(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/reports/maintenance-history`, { params });
      expect(result).toEqual(mockData);
    });

    it('getAssetSummary calls axios.get with correct url', async () => {
      const mockData = { data: {} };
      axios.get.mockResolvedValueOnce(mockData);
      const id = 1;
      const result = await getAssetSummary(id);
      expect(axios.get).toHaveBeenCalledWith(`${API}/reports/asset-summary/${id}`);
      expect(result).toEqual(mockData);
    });
  });

  describe('External', () => {
    it('getExternalInvoices calls axios.get with correct url', async () => {
      const mockData = { data: [] };
      axios.get.mockResolvedValueOnce(mockData);
      const serverIndex = 1;
      const result = await getExternalInvoices(serverIndex);
      expect(axios.get).toHaveBeenCalledWith(`${API}/external/invoices/${serverIndex}`);
      expect(result).toEqual(mockData);
    });

    it('searchExternalInvoice calls axios.get with correct url', async () => {
      const mockData = { data: {} };
      axios.get.mockResolvedValueOnce(mockData);
      const invoiceNumber = 'INV-123';
      const result = await searchExternalInvoice(invoiceNumber);
      expect(axios.get).toHaveBeenCalledWith(`${API}/external/search-invoice/${invoiceNumber}`);
      expect(result).toEqual(mockData);
    });
  });
});
