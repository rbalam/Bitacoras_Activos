import axios from 'axios';

// Set up env variables before importing api
process.env.REACT_APP_BACKEND_URL = 'http://localhost:8000';

const { createAsset } = require('../api');

jest.mock('axios');

describe('API Utils - createAsset', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should call axios.post with correct URL and data', async () => {
    const mockData = { name: 'Test Asset', type: 'equipment' };
    const mockResponse = { data: { id: 1, ...mockData } };

    axios.post.mockResolvedValueOnce(mockResponse);

    const result = await createAsset(mockData);

    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/assets',
      mockData
    );
    expect(result).toEqual(mockResponse);
  });

  it('should handle API errors correctly', async () => {
    const mockData = { name: 'Invalid Asset' };
    const mockError = new Error('Network Error');

    axios.post.mockRejectedValueOnce(mockError);

    await expect(createAsset(mockData)).rejects.toThrow('Network Error');

    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/assets',
      mockData
    );
  });
});
