import axios from 'axios';
import {
  getMaintenances,
  createMaintenance,
  updateMaintenance
} from './api';

// Mock axios
jest.mock('axios');

describe('Maintenance API Utils', () => {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getMaintenances', () => {
    it('should call axios.get with correct URL and params', async () => {
      const mockParams = { page: 1, limit: 10 };
      const mockResponse = { data: [{ id: 1, name: 'Test Maintenance' }] };
      axios.get.mockResolvedValueOnce(mockResponse);

      const response = await getMaintenances(mockParams);

      expect(axios.get).toHaveBeenCalledTimes(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenances`, { params: mockParams });
      expect(response).toEqual(mockResponse);
    });

    it('should call axios.get with correct URL without params', async () => {
      const mockResponse = { data: [] };
      axios.get.mockResolvedValueOnce(mockResponse);

      const response = await getMaintenances();

      expect(axios.get).toHaveBeenCalledTimes(1);
      expect(axios.get).toHaveBeenCalledWith(`${API}/maintenances`, { params: undefined });
      expect(response).toEqual(mockResponse);
    });
  });

  describe('createMaintenance', () => {
    it('should call axios.post with correct URL and data', async () => {
      const mockData = { name: 'New Maintenance', date: '2023-10-27' };
      const mockResponse = { data: { id: 2, ...mockData } };
      axios.post.mockResolvedValueOnce(mockResponse);

      const response = await createMaintenance(mockData);

      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(`${API}/maintenances`, mockData);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('updateMaintenance', () => {
    it('should call axios.put with correct URL and data', async () => {
      const mockId = 123;
      const mockData = { status: 'completed' };
      const mockResponse = { data: { id: mockId, ...mockData } };
      axios.put.mockResolvedValueOnce(mockResponse);

      const response = await updateMaintenance(mockId, mockData);

      expect(axios.put).toHaveBeenCalledTimes(1);
      expect(axios.put).toHaveBeenCalledWith(`${API}/maintenances/${mockId}`, mockData);
      expect(response).toEqual(mockResponse);
    });
  });
});
