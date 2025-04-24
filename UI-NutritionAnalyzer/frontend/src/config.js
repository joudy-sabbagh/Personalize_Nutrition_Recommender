/**
 * Application configuration
 */

// API configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Feature flags
export const FEATURES = {
  GLUCOSE_PREDICTION: true,
  MEAL_RECOMMENDATIONS: true,
  NUTRITIONAL_INSIGHTS: true,
  MICROBIOME_ANALYSIS: true,
};

// UI configuration
export const UI_CONFIG = {
  THEME_COLOR: '#4CAF50', // Primary theme color
  MAX_UPLOAD_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_IMAGE_FORMATS: ['image/jpeg', 'image/png', 'image/jpg'],
  SUPPORTED_DATA_FORMATS: ['.csv', '.xlsx', '.json'],
};

// Meal categories
export const MEAL_CATEGORIES = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snack', label: 'Snack' },
];

// Nutrient display settings
export const NUTRIENT_DISPLAY = {
  PRIMARY_NUTRIENTS: ['calories', 'carbohydrates', 'protein', 'fat'],
  DETAILED_NUTRIENTS: ['fiber', 'sugar', 'saturatedFat', 'sodium', 'potassium'],
  UNITS: {
    calories: 'kcal',
    carbohydrates: 'g',
    protein: 'g',
    fat: 'g',
    fiber: 'g',
    sugar: 'g',
    saturatedFat: 'g',
    sodium: 'mg',
    potassium: 'mg',
  },
};

// Glucose prediction settings
export const GLUCOSE_PREDICTION = {
  TIME_INTERVALS: [30, 60, 120], // Minutes after meal
  THRESHOLD_HIGH: 140, // mg/dL
  THRESHOLD_NORMAL: 100, // mg/dL
}; 