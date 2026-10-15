import axios from 'axios';
import * as api from './api';

jest.mock('axios');

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

describe('api functions', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Assets', () => {
    it('getAssets should make a GET request to /assets', async () => {
      const params = { page: 1 };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getAssets(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/assets`, { params });
    });

    it('getAsset should make a GET request to /assets/:id', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.getAsset(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/assets/1`);
    });

    it('createAsset should make a POST request to /assets', async () => {
      const data = { name: 'New Asset' };
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.createAsset(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/assets`, data);
    });

    it('updateAsset should make a PUT request to /assets/:id', async () => {
      const data = { name: 'Updated Asset' };
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.updateAsset(1, data);
      expect(axios.put).toHaveBeenCalledWith(`${API}/assets/1`, data);
    });
  });

  describe('Maintenances', () => {
    it('getMaintenances should make a GET request to /maintenances', async () => {
      const params = { status: 'pending' };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getMaintenances(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenances`, { params });
    });

    it('createMaintenance should make a POST request to /maintenances', async () => {
      const data = { description: 'New Maintenance' };
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.createMaintenance(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/maintenances`, data);
    });

    it('updateMaintenance should make a PUT request to /maintenances/:id', async () => {
      const data = { description: 'Updated Maintenance' };
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.updateMaintenance(1, data);
      expect(axios.put).toHaveBeenCalledWith(`${API}/maintenances/1`, data);
    });
  });

  describe('Maintenance Plans', () => {
    it('getMaintenancePlans should make a GET request to /maintenance-plans', async () => {
      const params = { type: 'preventive' };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getMaintenancePlans(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenance-plans`, { params });
    });

    it('getMaintenancePlan should make a GET request to /maintenance-plans/:id', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.getMaintenancePlan(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenance-plans/1`);
    });

    it('createMaintenancePlan should make a POST request to /maintenance-plans', async () => {
      const data = { name: 'New Plan' };
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.createMaintenancePlan(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/maintenance-plans`, data);
    });

    it('updateMaintenancePlan should make a PUT request to /maintenance-plans/:id', async () => {
      const data = { name: 'Updated Plan' };
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.updateMaintenancePlan(1, data);
      expect(axios.put).toHaveBeenCalledWith(`${API}/maintenance-plans/1`, data);
    });

    it('deleteMaintenancePlan should make a DELETE request to /maintenance-plans/:id', async () => {
      axios.delete.mockResolvedValueOnce({ data: {} });
      await api.deleteMaintenancePlan(1);
      expect(axios.delete).toHaveBeenCalledWith(`${API}/maintenance-plans/1`);
    });
  });

  describe('Quotes', () => {
    it('getQuotes should make a GET request to /quotes', async () => {
      const params = { status: 'open' };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getQuotes(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/quotes`, { params });
    });

    it('createQuote should make a POST request to /quotes', async () => {
      const data = { total: 100 };
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.createQuote(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/quotes`, data);
    });
  });

  describe('Authorizations', () => {
    it('getAuthorizations should make a GET request to /authorizations', async () => {
      const params = { type: 'repair' };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getAuthorizations(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/authorizations`, { params });
    });

    it('createAuthorization should make a POST request to /authorizations', async () => {
      const data = { requestedBy: 'user1' };
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.createAuthorization(data);
      expect(axios.post).toHaveBeenCalledWith(`${API}/authorizations`, data);
    });

    it('approveAuthorization should make a PUT request to /authorizations/:id/approve', async () => {
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.approveAuthorization(1, 'Looks good', true);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/1/approve`, null, {
        params: { comentarios: 'Looks good', notificar_whatsapp: true }
      });
    });

    it('rejectAuthorization should make a PUT request to /authorizations/:id/reject', async () => {
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.rejectAuthorization(1, 'Not enough info', false);
      expect(axios.put).toHaveBeenCalledWith(`${API}/authorizations/1/reject`, null, {
        params: { comentarios: 'Not enough info', notificar_whatsapp: false }
      });
    });
  });

  describe('Alerts', () => {
    it('getAlerts should make a GET request to /alerts', async () => {
      const params = { severity: 'high' };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getAlerts(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/alerts`, { params });
    });

    it('markAlertRead should make a PUT request to /alerts/:id/mark-read', async () => {
      axios.put.mockResolvedValueOnce({ data: {} });
      await api.markAlertRead(1);
      expect(axios.put).toHaveBeenCalledWith(`${API}/alerts/1/mark-read`);
    });
  });

  describe('Files', () => {
    it('uploadFile should make a POST request to /upload with multipart/form-data header', async () => {
      const formData = new FormData();
      formData.append('file', 'dummy_file');
      axios.post.mockResolvedValueOnce({ data: {} });
      await api.uploadFile(formData);
      expect(axios.post).toHaveBeenCalledWith(`${API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    });

    it('getFiles should make a GET request to /files/:entityType/:entityId', async () => {
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getFiles('asset', 1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/files/asset/1`);
    });

    it('downloadFile should return the correct URL string', () => {
      const url = api.downloadFile(1);
      expect(url).toEqual(`${API}/download/1`);
    });
  });

  describe('Analytics', () => {
    it('getDashboardStats should make a GET request to /analytics/dashboard', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.getDashboardStats();
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/dashboard`);
    });

    it('getAssetCosts should make a GET request to /analytics/asset/:id/costs', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.getAssetCosts(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/1/costs`);
    });

    it('checkAssetReplacement should make a GET request to /analytics/asset/:id/replacement-check', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.checkAssetReplacement(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/1/replacement-check`);
    });
  });

  describe('Reports', () => {
    it('getMaintenanceHistory should make a GET request to /reports/maintenance-history', async () => {
      const params = { year: 2023 };
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getMaintenanceHistory(params);
      expect(axios.get).toHaveBeenCalledWith(`${API}/reports/maintenance-history`, { params });
    });

    it('getAssetSummary should make a GET request to /reports/asset-summary/:id', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.getAssetSummary(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/reports/asset-summary/1`);
    });
  });

  describe('External', () => {
    it('getExternalInvoices should make a GET request to /external/invoices/:serverIndex', async () => {
      axios.get.mockResolvedValueOnce({ data: [] });
      await api.getExternalInvoices('server1');
      expect(axios.get).toHaveBeenCalledWith(`${API}/external/invoices/server1`);
    });

    it('searchExternalInvoice should make a GET request to /external/search-invoice/:invoiceNumber', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      await api.searchExternalInvoice('INV-123');
      expect(axios.get).toHaveBeenCalledWith(`${API}/external/search-invoice/INV-123`);
    });
  });
});
