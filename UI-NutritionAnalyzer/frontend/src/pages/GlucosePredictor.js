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
  Step,
  StepLabel,
  Stepper,
  IconButton,
  Tooltip,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon,
  Done as DoneIcon,
  Timeline as TimelineIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  RestaurantMenu as MealIcon
} from '@mui/icons-material';
import { useAlert } from '../context/AlertContext';
import { predictGlucoseFromMeal } from '../services/mealService';

const GlucosePredictor = () => {
  const { success, error } = useAlert();
  
  // Files state
  const [mealImage, setMealImage] = useState(null);
  const [mealImagePreview, setMealImagePreview] = useState('');
  const [bioFile, setBioFile] = useState(null);
  const [microFile, setMicroFile] = useState(null);
  
  // Form state
  const [mealCategory, setMealCategory] = useState('lunch');
  
  // UI state
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  
  const steps = ['Upload User Data', 'Meal Information', 'Prediction Results'];
  
  const handleFileChange = (setter, previewSetter = null) => (event) => {
    const file = event.target.files[0];
    if (file) {
      setter(file);
      if (previewSetter && file.type.startsWith('image/')) {
        previewSetter(URL.createObjectURL(file));
      }
    }
  };
  
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };
  
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  
  const handleReset = () => {
    setActiveStep(0);
    setMealImage(null);
    setMealImagePreview('');
    setBioFile(null);
    setMicroFile(null);
    setMealCategory('lunch');
    setResults(null);
  };
  
  const handleSubmit = async () => {
    if (!mealImage || !bioFile || !microFile) {
      error('Please provide all required files');
      return;
    }
    
    setLoading(true);
    console.log('Starting glucose prediction with:', {
      mealImageName: mealImage?.name,
      mealImageType: mealImage?.type,
      mealImageSize: mealImage?.size,
      bioFileName: bioFile?.name,
      bioFileType: bioFile?.type,
      bioFileSize: bioFile?.size,
      microFileName: microFile?.name,
      microFileType: microFile?.type,
      microFileSize: microFile?.size,
      mealCategory
    });
    
    try {
      console.log('Sending request to predictGlucoseFromMeal...');
      const response = await predictGlucoseFromMeal(
        mealImage,
        bioFile,
        microFile,
        mealCategory
      );
      
      console.log('Received response from predictGlucoseFromMeal:', response);
      
      if (response.error) {
        console.error('Error in response:', response.error);
        error(response.error || response.message || 'Failed to predict glucose response');
        return;
      }
      
      setResults(response);
      setActiveStep(2);
      success('Glucose prediction complete!');
    } catch (err) {
      console.error('Exception in handleSubmit:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      error(err.response?.data?.error || err.response?.data?.message || 'Failed to predict glucose response');
    } finally {
      setLoading(false);
    }
  };
  
  const isStepValid = (step) => {
    switch (step) {
      case 0:
        return bioFile && microFile;
      case 1:
        return mealImage;
      default:
        return true;
    }
  };
  
  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Clinical Data
                    <Tooltip title="Upload your clinical data CSV file containing information like age, gender, weight, etc.">
                      <IconButton size="small">
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                  
                  <Box
                    sx={{
                      border: '2px dashed #cccccc',
                      borderRadius: 2,
                      p: 3,
                      textAlign: 'center',
                      backgroundColor: 'grey.50',
                      cursor: 'pointer',
                      mb: 2,
                      height: 180,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                    }}
                    onClick={() => document.getElementById('upload-bio-file').click()}
                  >
                    {bioFile ? (
                      <Box sx={{ width: '100%' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                          <Typography variant="body1" color="primary" fontWeight="medium">
                            {bioFile.name}
                          </Typography>
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              setBioFile(null);
                            }}
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {(bioFile.size / 1024).toFixed(2)} KB
                        </Typography>
                        <Chip 
                          label="CSV File" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    ) : (
                      <>
                        <UploadIcon
                          sx={{
                            fontSize: 40,
                            color: 'primary.main',
                            mb: 1,
                          }}
                        />
                        <Typography variant="body1" gutterBottom>
                          Click to upload clinical data
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          CSV format required
                        </Typography>
                      </>
                    )}
                    <input
                      id="upload-bio-file"
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange(setBioFile)}
                      style={{ display: 'none' }}
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    The clinical data file should contain information such as age, gender, BMI, and other health metrics.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Microbiome Data
                    <Tooltip title="Upload your microbiome data CSV file containing gut bacteria composition">
                      <IconButton size="small">
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                  
                  <Box
                    sx={{
                      border: '2px dashed #cccccc',
                      borderRadius: 2,
                      p: 3,
                      textAlign: 'center',
                      backgroundColor: 'grey.50',
                      cursor: 'pointer',
                      mb: 2,
                      height: 180,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                    }}
                    onClick={() => document.getElementById('upload-micro-file').click()}
                  >
                    {microFile ? (
                      <Box sx={{ width: '100%' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                          <Typography variant="body1" color="primary" fontWeight="medium">
                            {microFile.name}
                          </Typography>
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              setMicroFile(null);
                            }}
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {(microFile.size / 1024).toFixed(2)} KB
                        </Typography>
                        <Chip 
                          label="CSV File" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    ) : (
                      <>
                        <UploadIcon
                          sx={{
                            fontSize: 40,
                            color: 'primary.main',
                            mb: 1,
                          }}
                        />
                        <Typography variant="body1" gutterBottom>
                          Click to upload microbiome data
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          CSV format required
                        </Typography>
                      </>
                    )}
                    <input
                      id="upload-micro-file"
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange(setMicroFile)}
                      style={{ display: 'none' }}
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    The microbiome data file should contain information about your gut bacteria composition, typically from a gut health test.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      case 1:
        return (
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
                      height: 250,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      mb: 2,
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                    onClick={() => document.getElementById('upload-meal-image').click()}
                  >
                    {mealImagePreview ? (
                      <>
                        <img
                          src={mealImagePreview}
                          alt="Meal preview"
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
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
                            setMealImage(null);
                            setMealImagePreview('');
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
                          Click to upload meal photo
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          JPG, PNG formats accepted
                        </Typography>
                      </>
                    )}
                    <input
                      id="upload-meal-image"
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange(setMealImage, setMealImagePreview)}
                      style={{ display: 'none' }}
                    />
                  </Box>
                  
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel id="meal-category-label">Meal Category</InputLabel>
                    <Select
                      labelId="meal-category-label"
                      value={mealCategory}
                      label="Meal Category"
                      onChange={(e) => setMealCategory(e.target.value)}
                    >
                      <MenuItem value="breakfast">Breakfast</MenuItem>
                      <MenuItem value="lunch">Lunch</MenuItem>
                      <MenuItem value="dinner">Dinner</MenuItem>
                      <MenuItem value="snack">Snack</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    How It Works
                  </Typography>
                  
                  <Typography variant="body2" paragraph>
                    Our glucose prediction system combines:
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <MealIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="body2">
                      <strong>Meal Analysis:</strong> We identify the nutritional content of your meal from the photo.
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TimelineIcon color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="body2">
                      <strong>Clinical Data:</strong> Your age, gender, and health metrics help personalize predictions.
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <InfoIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="body2">
                      <strong>Microbiome Profile:</strong> Your unique gut bacteria influence how you process different foods.
                    </Typography>
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="body2" paragraph>
                    After analyzing all factors, we predict how your glucose levels will respond to this specific meal, giving you insights for better food choices.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      case 2:
        if (loading) {
          return (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <CircularProgress size={60} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Generating Predictions...
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                This may take a moment as we analyze your data
              </Typography>
            </Box>
          );
        }
        
        if (!results) {
          return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No results yet. Please complete the prediction process.
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => setActiveStep(0)}
                sx={{ mt: 2 }}
              >
                Start Over
              </Button>
            </Box>
          );
        }
        
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5">
                      Glucose Response Prediction
                    </Typography>
                    <Chip 
                      label={`Meal Category: ${mealCategory.charAt(0).toUpperCase() + mealCategory.slice(1)}`} 
                      color="primary" 
                      variant="outlined" 
                    />
                  </Box>
                  
                  <Grid container spacing={4}>
                    <Grid item xs={12} md={6}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                        {mealImagePreview && (
                          <Paper 
                            elevation={0} 
                            sx={{ 
                              width: 120, 
                              height: 120, 
                              borderRadius: 2, 
                              overflow: 'hidden',
                              mr: 3,
                              flexShrink: 0
                            }}
                          >
                            <img 
                              src={mealImagePreview} 
                              alt="Meal" 
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                            />
                          </Paper>
                        )}
                        
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {results.caption || 'Analyzed Meal'}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                            <Chip
                              label={`Carbs: ${results.nutrition.carbs_pct}%`}
                              size="small"
                              color="primary"
                            />
                            <Chip
                              label={`Protein: ${results.nutrition.protein_pct}%`}
                              size="small"
                              color="secondary"
                            />
                            <Chip
                              label={`Fat: ${results.nutrition.fat_pct}%`}
                              size="small"
                              color="default"
                            />
                          </Box>
                        </Box>
                      </Box>
                      
                      <Divider sx={{ my: 3 }} />
                      
                      <Typography variant="subtitle1" gutterBottom>
                        Predicted Glucose Response
                      </Typography>
                      
                      <Grid container spacing={3}>
                        <Grid item xs={12} sm={6}>
                          <Paper
                            elevation={0}
                            sx={{
                              p: 2,
                              backgroundColor: 'grey.50',
                              borderRadius: 2,
                              textAlign: 'center',
                            }}
                          >
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              After 30 Minutes
                            </Typography>
                            <Typography 
                              variant="h3" 
                              color={results.glucose_prediction.spike_30min > 40 ? 'error.main' : 
                                     results.glucose_prediction.spike_30min > 20 ? 'warning.main' : 'success.main'}
                            >
                              {results.glucose_prediction.spike_30min}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              mg/dL
                            </Typography>
                          </Paper>
                        </Grid>
                        
                        <Grid item xs={12} sm={6}>
                          <Paper
                            elevation={0}
                            sx={{
                              p: 2,
                              backgroundColor: 'grey.50',
                              borderRadius: 2,
                              textAlign: 'center',
                            }}
                          >
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              After 60 Minutes
                            </Typography>
                            <Typography 
                              variant="h3" 
                              color={results.glucose_prediction.spike_60min > 40 ? 'error.main' : 
                                     results.glucose_prediction.spike_60min > 20 ? 'warning.main' : 'success.main'}
                            >
                              {results.glucose_prediction.spike_60min}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              mg/dL
                            </Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Paper elevation={0} sx={{ p: 3, backgroundColor: 'grey.50', borderRadius: 2 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          Key Insights
                        </Typography>
                        
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" gutterBottom>
                            Impact Level
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <Box sx={{ width: '100%', mr: 1 }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={Math.min(results.glucose_prediction.impact_score * 10, 100)} 
                                color={results.glucose_prediction.impact_score > 7 ? "error" : 
                                      results.glucose_prediction.impact_score > 4 ? "warning" : "success"}
                                sx={{ height: 10, borderRadius: 5 }}
                              />
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                              {results.glucose_prediction.impact_score}/10
                            </Typography>
                          </Box>
                        </Box>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          {results.glucose_prediction.recommendation || 
                           "Based on your unique profile, this meal will produce a moderate glucose response. Consider balancing with physical activity after eating."}
                        </Typography>
                        
                        <Divider sx={{ my: 2 }} />
                        
                        <Typography variant="subtitle2" gutterBottom>
                          Personal Factors
                        </Typography>
                        
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                          {results.glucose_prediction.factors && results.glucose_prediction.factors.map((factor, index) => (
                            <Chip
                              key={index}
                              label={factor}
                              size="small"
                              color={index % 3 === 0 ? "primary" : index % 3 === 1 ? "secondary" : "default"}
                              variant="outlined"
                              sx={{ m: 0.5 }}
                            />
                          ))}
                          {(!results.glucose_prediction.factors || results.glucose_prediction.factors.length === 0) && (
                            <Typography variant="body2" color="text.secondary">
                              Standard metabolic response expected
                            </Typography>
                          )}
                        </Box>
                      </Paper>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                        <Button 
                          variant="outlined"
                          onClick={handleReset}
                          sx={{ mr: 2 }}
                        >
                          Start New Prediction
                        </Button>
                        <Button 
                          variant="contained"
                          color="secondary"
                        >
                          Save Results
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      default:
        return (
          <Typography>Unknown step</Typography>
        );
    }
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Glucose Response Predictor
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Predict how your glucose levels will respond to specific meals based on your personal data.
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      {renderStepContent(activeStep)}
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          color="inherit"
          disabled={activeStep === 0 || activeStep === 2}
          onClick={handleBack}
          startIcon={<BackIcon />}
        >
          Back
        </Button>
        
        <Box>
          {activeStep === steps.length - 1 ? (
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleReset}
            >
              Start New Prediction
            </Button>
          ) : activeStep === steps.length - 2 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={!isStepValid(activeStep) || loading}
              endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <DoneIcon />}
            >
              {loading ? 'Processing...' : 'Complete Prediction'}
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={handleNext}
              disabled={!isStepValid(activeStep)}
              endIcon={<NextIcon />}
            >
              Next
            </Button>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default GlucosePredictor; 