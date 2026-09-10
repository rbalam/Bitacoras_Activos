import axios from 'axios';
import { getAssets } from './api';

jest.mock('axios');

describe('API utils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAssets', () => {
    it('should call axios.get with correct URL and params', async () => {
      const mockParams = { page: 1, limit: 10 };
      const mockResponse = { data: { assets: [] } };
      axios.get.mockResolvedValue(mockResponse);

      const result = await getAssets(mockParams);

      expect(axios.get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/assets$/), { params: mockParams });
      expect(result).toEqual(mockResponse);
    });

    it('should handle call when no params are provided', async () => {
      const mockResponse = { data: { assets: [] } };
      axios.get.mockResolvedValue(mockResponse);

      const result = await getAssets();

      expect(axios.get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/assets$/), { params: undefined });
      expect(result).toEqual(mockResponse);
    });

    it('should handle an error response', async () => {
      const mockError = new Error('Network Error');
      axios.get.mockRejectedValue(mockError);

      await expect(getAssets()).rejects.toThrow('Network Error');
      expect(axios.get).toHaveBeenCalledWith(expect.stringMatching(/\/api\/assets$/), { params: undefined });
    });
  });
});
