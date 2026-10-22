import axios from 'axios';
import { updateAsset } from '../api';

jest.mock('axios');

describe('API Utils - Assets', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('updateAsset', () => {
    it('should call axios.put with the correct URL and data', async () => {
      const mockId = 123;
      const mockData = { name: 'Updated Asset', status: 'active' };
      const mockResponse = { data: { id: 123, name: 'Updated Asset', status: 'active' } };

      axios.put.mockResolvedValueOnce(mockResponse);

      const response = await updateAsset(mockId, mockData);

      expect(axios.put).toHaveBeenCalledTimes(1);

      const expectedUrl = `${process.env.REACT_APP_BACKEND_URL}/api/assets/${mockId}`;
      expect(axios.put).toHaveBeenCalledWith(expectedUrl, mockData);
      expect(response).toEqual(mockResponse);
    });
  });
});
