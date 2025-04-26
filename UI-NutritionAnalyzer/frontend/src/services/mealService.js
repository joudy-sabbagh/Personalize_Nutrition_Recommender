import axios from 'axios';
import { API_BASE_URL } from '../config';

/**
 * Analyze a meal image and return nutritional information
 * @param {File} mealImage - The meal image file
 * @param {Object} options - Additional options like meal type
 * @returns {Promise<Object>} The meal analysis result
 */
export const analyzeMeal = async (mealImage, options = {}) => {
  const formData = new FormData();
  formData.append('image', mealImage);
  
  if (options.description) {
    formData.append('description', options.description);
  } else {
    formData.append('description', 'none');
  }
  
  const response = await axios.post(`${API_BASE_URL}/analyze-meal`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Predict glucose response for a meal
 * @param {File} mealImage - The meal image file
 * @param {File} bioFile - The clinical/biomarker data file
 * @param {File} microFile - The microbiome data file
 * @param {string} mealCategory - The meal category (breakfast, lunch, dinner, snack)
 * @param {string} description - Optional description of the meal
 * @returns {Promise<Object>} The glucose prediction result
 */
export const predictGlucoseFromMeal = async (mealImage, bioFile, microFile, mealCategory, description = '') => {
  console.log('predictGlucoseFromMeal called with:', {
    endpoint: `${API_BASE_URL}/predict-glucose-from-all`,
    mealImageName: mealImage?.name,
    bioFileName: bioFile?.name,
    microFileName: microFile?.name,
    mealCategory,
    description
  });

  const formData = new FormData();
  formData.append('image', mealImage);
  formData.append('bio_file', bioFile);
  formData.append('micro_file', microFile);
  formData.append('meal_category', mealCategory);
  
  if (description) {
    formData.append('description', description);
  } else {
    formData.append('description', 'none');
  }
  
  try {
    console.log('Sending API request to predict glucose...');
    console.log('API URL:', `${API_BASE_URL}/predict-glucose-from-all`);
    console.log('FormData keys:', [...formData.keys()]);
    
    const response = await axios.post(`${API_BASE_URL}/predict-glucose-from-all`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('Glucose prediction API response status:', response.status);
    console.log('Glucose prediction API response headers:', response.headers);
    console.log('Glucose prediction API response data (full):', JSON.stringify(response.data, null, 2));
    
    // Log specific parts of the response for easier debugging
    if (response.data) {
      console.log('Response contains nutrition data:', !!response.data.nutrition);
      console.log('Response contains glucose_prediction data:', !!response.data.glucose_prediction);
      
      if (response.data.nutrition) {
        console.log('Nutrition data keys:', Object.keys(response.data.nutrition));
      }
      
      if (response.data.glucose_prediction) {
        console.log('Glucose prediction data keys:', Object.keys(response.data.glucose_prediction));
        console.log('glucose_spike_60min value:', response.data.glucose_prediction.glucose_spike_60min);
        console.log('message value:', response.data.glucose_prediction.message);
      }
      
      if (response.data.error) {
        console.error('Error in response:', response.data.error);
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('Error in predictGlucoseFromMeal:', error);
    console.error('Error response:', error.response?.data);
    console.error('Error status:', error.response?.status);
    throw error;
  }
};

/**
 * Get meal recommendations based on meal caption and user goal
 * @param {string} caption - The meal caption/description
 * @param {string} mealType - The meal type (breakfast, lunch, dinner, snack)
 * @param {string} nutritionGoal - The user's nutrition goal (bulking, cutting, maintaining)
 * @returns {Promise<Object>} The meal recommendations
 */
export const getMealRecommendations = async (caption, mealType, nutritionGoal) => {
  const response = await axios.post(`${API_BASE_URL}/recommend-meal`, {
    user_id: 'default-user', // This can be updated with actual user ID when authentication is implemented
    meal_type: mealType,
    nutrition_goal: nutritionGoal,
    caption: caption
  }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  return response.data;
};

/**
 * Predict gut health from microbiome data
 * @param {File} microbiomeFile - The microbiome data file
 * @returns {Promise<Object>} The gut health prediction result
 */
export const predictGutHealth = async (microbiomeFile) => {
  const formData = new FormData();
  formData.append('file', microbiomeFile);
  
  const response = await axios.post(`${API_BASE_URL}/predict-gut-health`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * Save a meal and its analysis to the user's history
 * @param {Object} mealData - The meal data including nutrition, glucose prediction and image
 * @returns {Promise<Object>} The saved meal record
 */
export const saveMealRecord = async (mealData) => {
  const response = await axios.post(`${API_BASE_URL}/api/meals/save`, mealData, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  return response.data;
};

