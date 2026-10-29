import axios from 'axios';
import { getAssets, getAsset, createAsset, updateAsset } from './api';

jest.mock('axios');

describe('API Utils - Assets', () => {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getAssets', () => {
    it('should call axios.get with the correct URL and params', async () => {
      const mockParams = { page: 1, limit: 10 };
      const mockResponse = { data: [{ id: 1, name: 'Asset 1' }] };
      axios.get.mockResolvedValueOnce(mockResponse);

      const response = await getAssets(mockParams);

      expect(axios.get).toHaveBeenCalledWith(`${API}/assets`, { params: mockParams });
      expect(response).toEqual(mockResponse);
    });

    it('should call axios.get with the correct URL without params', async () => {
      const mockResponse = { data: [{ id: 1, name: 'Asset 1' }] };
      axios.get.mockResolvedValueOnce(mockResponse);

      const response = await getAssets();

      expect(axios.get).toHaveBeenCalledWith(`${API}/assets`, { params: undefined });
      expect(response).toEqual(mockResponse);
    });
  });

  describe('getAsset', () => {
    it('should call axios.get with the correct URL for a specific asset ID', async () => {
      const mockId = 123;
      const mockResponse = { data: { id: mockId, name: 'Asset 123' } };
      axios.get.mockResolvedValueOnce(mockResponse);

      const response = await getAsset(mockId);

      expect(axios.get).toHaveBeenCalledWith(`${API}/assets/${mockId}`);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('createAsset', () => {
    it('should call axios.post with the correct URL and data', async () => {
      const mockData = { name: 'New Asset', type: 'Machinery' };
      const mockResponse = { data: { id: 1, ...mockData } };
      axios.post.mockResolvedValueOnce(mockResponse);

      const response = await createAsset(mockData);

      expect(axios.post).toHaveBeenCalledWith(`${API}/assets`, mockData);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('updateAsset', () => {
    it('should call axios.put with the correct URL and data for a specific asset ID', async () => {
      const mockId = 123;
      const mockData = { name: 'Updated Asset' };
      const mockResponse = { data: { id: mockId, ...mockData } };
      axios.put.mockResolvedValueOnce(mockResponse);

      const response = await updateAsset(mockId, mockData);

      expect(axios.put).toHaveBeenCalledWith(`${API}/assets/${mockId}`, mockData);
      expect(response).toEqual(mockResponse);
    });
  });
});
