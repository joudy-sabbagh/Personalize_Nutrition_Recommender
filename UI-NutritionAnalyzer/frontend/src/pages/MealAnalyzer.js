import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  CircularProgress,
  Divider,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Chip,
  IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  RestaurantMenu as FoodIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAlert } from '../context/AlertContext';
import { analyzeMeal } from '../services/mealService';

// const NutrientChip = ({ label, value, color = 'primary', unit = 'g' }) => (
//   <Chip
//     label={`${label}: ${value}${unit}`}
//     color={color}
//     size="small"
//     sx={{ m: 0.5 }}
//   />
// );

const MealAnalyzer = () => {
  const { success, error } = useAlert();
  
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('image/')) {
        setFile(selectedFile);
        setFilePreview(URL.createObjectURL(selectedFile));
      } else {
        error('Please upload an image file (JPEG, PNG, etc.)');
      }
    }
  };
  
  const handleDrop = (event) => {
    event.preventDefault();
    
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      setFile(droppedFile);
      setFilePreview(URL.createObjectURL(droppedFile));
    } else {
      error('Please upload an image file (JPEG, PNG, etc.)');
    }
  };
  
  const handleDragOver = (event) => {
    event.preventDefault();
  };
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!file) {
      error('Please upload an image of your meal');
      return;
    }
    
    setLoading(true);
    
    try {
      // Pass meal description if available
      const options = description ? { description } : {};
      const response = await analyzeMeal(file, options);
      
      if (response.error) {
        error(response.error || response.message || 'Failed to analyze meal');
        return;
      }
      
      // Extract nutrition data from the response
      console.log('API Response:', response);
      
      // The nutrition data is nested - need to correctly extract it
      const nutritionData = response.nutrition?.nutrition || {};
      console.log('Extracted nutrition data:', nutritionData);
      
      setResults(nutritionData);
      success('Meal analyzed successfully!');
    } catch (err) {
      console.error('Error analyzing meal:', err);
      error(err.response?.data?.error || err.response?.data?.message || 'Failed to analyze meal');
    } finally {
      setLoading(false);
    }
  };
  
  const resetForm = () => {
    setFile(null);
    setFilePreview('');
    setDescription('');
    setResults(null);
  };
  
  const renderResults = () => {
    if (!results) return null;
    
    console.log('Rendering results with data:', results);
    
    return (
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              Analysis Results
            </Typography>
            <IconButton onClick={resetForm} size="small">
              <RefreshIcon />
            </IconButton>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Macronutrients
              </Typography>
              <Paper elevation={0} sx={{ p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Carbohydrates
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {results.carbs_pct !== undefined ? `${results.carbs_pct}%` : '0%'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Protein
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {results.protein_pct !== undefined ? `${results.protein_pct}%` : '0%'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Fat
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {results.fat_pct !== undefined ? `${results.fat_pct}%` : '0%'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Health Metrics
              </Typography>
              
              <Paper elevation={0} sx={{ p: 2, backgroundColor: 'grey.50', borderRadius: 2, mb: 3 }}>
                <Typography variant="body2" gutterBottom>
                  Refined Carbs
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={results.refined_carb === 1 ? 100 : 0} 
                      color={results.refined_carb === 1 ? "warning" : "success"}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {results.refined_carb === 1 ? "present" : "not present"}
                  </Typography>
                </Box>
                
                <Typography variant="body2" gutterBottom sx={{ mt: 2 }}>
                  Sugar Risk
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={results.sugar_risk === 1 ? 100 : 0} 
                      color={results.sugar_risk === 1 ? "warning" : "success"}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {results.sugar_risk === 1 ? "high" : "low"}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="subtitle1" gutterBottom>
            Recommendations
          </Typography>
          <Typography variant="body2" paragraph>
            {results.recommendation || 'This meal appears balanced. It contains a good mix of nutrients and should provide sustained energy.'}
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button 
              variant="outlined" 
              color="primary"
              onClick={resetForm}
              startIcon={<RefreshIcon />}
            >
              Analyze Another Meal
            </Button>
            
            <Button 
              variant="contained" 
              color="secondary"
            >
              Save to History
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Meal Analyzer
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload a photo of your meal to analyze its nutritional content and potential glucose impact.
      </Typography>
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upload Meal Photo
                </Typography>
                
                <Box
                  sx={{
                    border: '2px dashed #cccccc',
                    borderRadius: 2,
                    p: 2,
                    textAlign: 'center',
                    backgroundColor: 'grey.50',
                    cursor: 'pointer',
                    height: 300,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    mb: 2,
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                  onClick={() => document.getElementById('upload-meal-image').click()}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                >
                  {filePreview ? (
                    <>
                      <img
                        src={filePreview}
                        alt="Meal preview"
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'contain',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                        }}
                      />
                      <IconButton
                        sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          backgroundColor: 'rgba(255, 255, 255, 0.7)',
                          '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.9)' },
                        }}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                          setFilePreview('');
                        }}
                      >
                        <CloseIcon />
                      </IconButton>
                    </>
                  ) : (
                    <>
                      <UploadIcon
                        sx={{
                          fontSize: 48,
                          color: 'primary.main',
                          mb: 2,
                        }}
                      />
                      <Typography variant="body1" gutterBottom>
                        Drag and drop your meal photo here
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        or click to browse files
                      </Typography>
                    </>
                  )}
                  <input
                    id="upload-meal-image"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                </Box>
                
                <TextField
                  fullWidth
                  label="Meal Description (Optional)"
                  placeholder="E.g., Grilled chicken salad with olive oil dressing"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  multiline
                  rows={2}
                  variant="outlined"
                  sx={{ mb: 2 }}
                />
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="meal-category-label">Meal Category</InputLabel>
                  <Select
                    labelId="meal-category-label"
                    value={results?.category || "lunch"}
                    label="Meal Category"
                    disabled={loading}
                  >
                    <MenuItem value="breakfast">Breakfast</MenuItem>
                    <MenuItem value="lunch">Lunch</MenuItem>
                    <MenuItem value="dinner">Dinner</MenuItem>
                    <MenuItem value="snack">Snack</MenuItem>
                  </Select>
                </FormControl>
                
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <FoodIcon />}
                  disabled={!file || loading}
                  sx={{ py: 1.5 }}
                >
                  {loading ? 'Analyzing...' : 'Analyze Meal'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            {loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <CircularProgress />
                <Typography variant="body1" sx={{ mt: 2 }}>
                  Analyzing your meal...
                </Typography>
              </Box>
            ) : (
              results ? renderResults() : (
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <FoodIcon sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No Analysis Yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" align="center">
                    Upload a photo of your meal and click "Analyze Meal" to see nutritional information and glucose impact.
                  </Typography>
                </Box>
              )
            )}
          </Grid>
        </Grid>
      </form>
    </Container>
  );
};

export default MealAnalyzer; 