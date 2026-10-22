import axios from 'axios';
import { createAsset } from './api';

jest.mock('axios');

describe('API Utils - createAsset', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should call axios.post with the correct URL and payload', async () => {
    const mockData = { name: 'New Asset', type: 'Equipment' };
    const mockResponse = { data: { id: 1, ...mockData } };

    axios.post.mockResolvedValueOnce(mockResponse);

    const response = await createAsset(mockData);

    const expectedUrl = `${process.env.REACT_APP_BACKEND_URL}/api/assets`;

    expect(axios.post).toHaveBeenCalledTimes(1);
    expect(axios.post).toHaveBeenCalledWith(expectedUrl, mockData);
    expect(response).toEqual(mockResponse);
  });
});
