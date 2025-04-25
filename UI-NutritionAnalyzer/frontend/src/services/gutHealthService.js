import apiClient from './api';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export const predictGutHealth = async (microbiomeFile) => {
  const formData = new FormData();
  formData.append('file', microbiomeFile);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/predict-gut-health`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting gut health:', error);
    throw error;
  }
}; 