import apiClient from './api';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export const predictGutHealth = async (microbiomeFile) => {
  const formData = new FormData();
  formData.append('file', microbiomeFile);
  
  console.log('Sending gut health analysis request with file:', microbiomeFile.name);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/predict-gut-health`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Gut health API response:', response.data);
    console.log('Response contains prediction:', response.data.prediction);
    console.log('Prediction value:', response.data.prediction);
    console.log('Probability:', response.data.probability_good);
    
    return response.data;
  } catch (error) {
    console.error('Error predicting gut health:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
}; 