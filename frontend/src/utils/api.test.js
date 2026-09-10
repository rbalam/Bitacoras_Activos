import axios from 'axios';
import { createAsset } from './api';

jest.mock('axios');

describe('API utils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createAsset', () => {
    it('should call axios.post with correct URL and payload', async () => {
      const mockData = { name: 'Test Asset', type: 'Equipment' };
      const expectedUrl = `${process.env.REACT_APP_BACKEND_URL}/api/assets`;

      const mockResponse = { data: { id: 1, ...mockData } };
      axios.post.mockResolvedValueOnce(mockResponse);

      const response = await createAsset(mockData);

      expect(axios.post).toHaveBeenCalledTimes(1);
      expect(axios.post).toHaveBeenCalledWith(expectedUrl, mockData);
      expect(response).toEqual(mockResponse);
    });
  });
});
