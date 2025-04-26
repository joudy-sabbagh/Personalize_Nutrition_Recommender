import apiClient from './api';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export const predictGutHealth = async (microbiomeFile) => {
  const formData = new FormData();
  formData.append('file', microbiomeFile);
  
  console.log('API endpoint:', `${API_BASE_URL}/predict-gut-health`);
  console.log('File being sent:', microbiomeFile.name, 'size:', microbiomeFile.size);
  
  try {
    console.log('Sending request to predict gut health...');
    const response = await axios.post(`${API_BASE_URL}/predict-gut-health`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Received gut health response - status:', response.status);
    console.log('Response headers:', response.headers);
    console.log('Response data:', response.data);
    
    if (response.data) {
      console.log('Response data type:', typeof response.data);
      if (typeof response.data === 'object') {
        console.log('Response data keys:', Object.keys(response.data));
        console.log('Prediction value in response:', response.data.prediction);
        console.log('Probability good value in response:', response.data.probability_good);
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('Error predicting gut health:', error);
    if (error.response) {
      console.error('Error response status:', error.response.status);
      console.error('Error response data:', error.response.data);
    }
    throw error;
  }
}; 