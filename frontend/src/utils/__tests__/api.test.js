import axios from 'axios';
import { getDashboardStats, getAssetCosts, checkAssetReplacement } from '../api';

jest.mock('axios');

describe('Analytics API', () => {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getDashboardStats', () => {
    it('should call axios.get with the correct URL', async () => {
      const mockData = { total_assets: 10, pending_maintenances: 5 };
      axios.get.mockResolvedValueOnce({ data: mockData });

      const result = await getDashboardStats();

      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/dashboard`);
      expect(axios.get).toHaveBeenCalledTimes(1);
      expect(result.data).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Network Error';
      axios.get.mockRejectedValueOnce(new Error(errorMessage));

      await expect(getDashboardStats()).rejects.toThrow(errorMessage);
    });
  });

  describe('getAssetCosts', () => {
    it('should call axios.get with the correct URL', async () => {
      const assetId = 123;
      const mockData = { total_cost: 1500, maintenance_cost: 500 };
      axios.get.mockResolvedValueOnce({ data: mockData });

      const result = await getAssetCosts(assetId);

      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/${assetId}/costs`);
      expect(axios.get).toHaveBeenCalledTimes(1);
      expect(result.data).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      const assetId = 123;
      const errorMessage = 'Network Error';
      axios.get.mockRejectedValueOnce(new Error(errorMessage));

      await expect(getAssetCosts(assetId)).rejects.toThrow(errorMessage);
    });
  });

  describe('checkAssetReplacement', () => {
    it('should call axios.get with the correct URL', async () => {
      const assetId = 456;
      const mockData = { needs_replacement: true, reason: 'High maintenance cost' };
      axios.get.mockResolvedValueOnce({ data: mockData });

      const result = await checkAssetReplacement(assetId);

      expect(axios.get).toHaveBeenCalledWith(`${API}/analytics/asset/${assetId}/replacement-check`);
      expect(axios.get).toHaveBeenCalledTimes(1);
      expect(result.data).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      const assetId = 456;
      const errorMessage = 'Network Error';
      axios.get.mockRejectedValueOnce(new Error(errorMessage));

      await expect(checkAssetReplacement(assetId)).rejects.toThrow(errorMessage);
    });
  });
});
