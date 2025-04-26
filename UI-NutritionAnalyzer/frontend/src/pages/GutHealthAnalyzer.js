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
  Paper,
  Divider,
  IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Science as ScienceIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useAlert } from '../context/AlertContext';
import { predictGutHealth } from '../services/gutHealthService';

const GutHealthAnalyzer = () => {
  const { success, error } = useAlert();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile);
      } else {
        error('Please upload a CSV file with microbiome data');
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!file) {
      error('Please upload your microbiome data file');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await predictGutHealth(file);
      console.log('Gut health API response:', response);
      console.log('Response type:', typeof response);
      console.log('Response keys:', Object.keys(response));
      console.log('Prediction value:', response.prediction);
      console.log('Probability good value:', response.probability_good);
      setResults(response);
      success('Gut health analysis completed successfully!');
    } catch (err) {
      console.error('Error in gut health analysis:', err);
      error(err.response?.data?.error || 'Failed to analyze microbiome data');
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;
    
    console.log('Rendering results:', results);
    console.log('Results type:', typeof results);
    console.log('Results prediction:', results.prediction);
    console.log('Results probability_good:', results.probability_good);
    
    const isGoodHealth = results.prediction === "Good";
    console.log('isGoodHealth evaluation:', isGoodHealth, '(prediction === "Good")');
    
    const healthMessage = isGoodHealth 
      ? "You currently have a healthy gut" 
      : "Prebiotic and probiotic foods like whole grains, onions, garlic, fermented foods, miso and yogurt feed the good bacteria in your gut. A diet rich with fiber and prebiotics ensures that the bacteria grows.";
    
    return (
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Your Gut Health Analysis
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Overall Gut Health Status
              </Typography>
              
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 3, 
                  textAlign: 'center',
                  backgroundColor: isGoodHealth ? '#e8f5e9' : '#ffebee'
                }}
              >
                <Typography variant="h2" color={isGoodHealth ? 'success.main' : 'error.main'}>
                  {results.prediction || "Unknown"}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Probability: {results.probability_good ? (results.probability_good * 100).toFixed(1) + "%" : "N/A"}
                </Typography>
              </Paper>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="body1" fontWeight="medium">
                  {healthMessage}
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Key Indicators
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body1">
                    Gut Microbiome Health
                  </Typography>
                  <Typography 
                    variant="body1" 
                    fontWeight="medium"
                    color={isGoodHealth ? 'success.main' : 'error.main'}
                  >
                    {results.prediction}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Overall assessment of your gut microbiome health
                </Typography>
                <Divider sx={{ mt: 1 }} />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body1">
                    Healthy Bacteria Probability
                  </Typography>
                  <Typography 
                    variant="body1" 
                    fontWeight="medium"
                    color={results.probability_good > 0.5 ? 'success.main' : 'error.main'}
                  >
                    {results.probability_good ? (results.probability_good * 100).toFixed(1) + "%" : "N/A"}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Likelihood of having good gut bacteria
                </Typography>
                <Divider sx={{ mt: 1 }} />
              </Box>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          
          <Typography variant="body1" paragraph>
            {isGoodHealth 
              ? "Your gut microbiome appears healthy. Continue maintaining a balanced diet with diverse plant foods, fermented products, and adequate fiber intake to support your gut health."
              : "Based on your gut microbiome profile, we recommend increasing your intake of prebiotic and probiotic foods. Focus on whole grains, onions, garlic, fermented foods like miso, kimchi, and yogurt to feed the good bacteria in your gut. A diet rich with fiber and prebiotics ensures that beneficial bacteria grows."}
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => {
                setFile(null);
                setResults(null);
              }}
            >
              Start New Analysis
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Gut Health Analyzer
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your microbiome data to analyze your gut health and get personalized recommendations.
      </Typography>
      
      {results && (
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Your Gut Health Analysis
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Overall Gut Health Status
                </Typography>
                
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    backgroundColor: results.prediction === "Good" ? '#e8f5e9' : '#ffebee'
                  }}
                >
                  <Typography variant="h2" color={results.prediction === "Good" ? 'success.main' : 'error.main'}>
                    {results.prediction}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {results.probability_good !== undefined && 
                      `Probability: ${(results.probability_good * 100).toFixed(1)}%`}
                  </Typography>
                </Paper>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="body1" fontWeight="medium">
                    {console.log('Rendering message for prediction:', results.prediction)}
                    {results.prediction === "Good" 
                      ? "You currently have a healthy gut":
                      results.prediction === "Bad" 
                      ?"Prebiotic and probiotic foods like whole grains, onions, garlic, fermented foods, miso and yogurt feed the good bacteria in your gut. A diet rich with fiber and prebiotics ensures that the bacteria grows."
                      : `Prediction: ${results.prediction || "Unknown"}`}
                      </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Key Indicators
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body1">
                      Gut Microbiome Health
                    </Typography>
                    <Typography 
                      variant="body1" 
                      fontWeight="medium"
                      color={results.prediction === "Good" ? 'success.main' : 'error.main'}
                    >
                      {results.prediction}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Overall assessment of your gut microbiome health
                  </Typography>
                  <Divider sx={{ mt: 1 }} />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body1">
                      Healthy Bacteria Probability
                    </Typography>
                    <Typography 
                      variant="body1" 
                      fontWeight="medium"
                      color={results.probability_good > 0.5 ? 'success.main' : 'error.main'}
                    >
                      {results.probability_good ? (results.probability_good * 100).toFixed(1) + "%" : "N/A"}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Likelihood of having good gut bacteria
                  </Typography>
                  <Divider sx={{ mt: 1 }} />
                </Box>
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            
            <Typography variant="body1" paragraph>
              {results.prediction === "Good" 
                ? "Your gut microbiome appears healthy. Continue maintaining a balanced diet with diverse plant foods, fermented products, and adequate fiber intake to support your gut health."
                : "Based on your gut microbiome profile, we recommend increasing your intake of prebiotic and probiotic foods. Focus on whole grains, onions, garlic, fermented foods like miso, kimchi, and yogurt to feed the good bacteria in your gut. A diet rich with fiber and prebiotics ensures that beneficial bacteria grows."}
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => {
                  setFile(null);
                  setResults(null);
                }}
              >
                Start New Analysis
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
      
      {!results && (
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upload Microbiome Data
                </Typography>
                
                <Box
                  sx={{
                    border: '2px dashed #cccccc',
                    borderRadius: 2,
                    p: 3,
                    textAlign: 'center',
                    backgroundColor: 'grey.50',
                    cursor: 'pointer',
                    mb: 3,
                    height: 200,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    position: 'relative',
                  }}
                  onClick={() => document.getElementById('upload-microbiome-data').click()}
                >
                  {file ? (
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="body1" color="primary" fontWeight="medium">
                          {file.name}
                        </Typography>
                        <IconButton 
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            setFile(null);
                          }}
                        >
                          <CloseIcon fontSize="small" />
                        </IconButton>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {(file.size / 1024).toFixed(2)} KB
                      </Typography>
                    </Box>
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
                        Upload your microbiome data
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        CSV format required
                      </Typography>
                    </>
                  )}
                  <input
                    id="upload-microbiome-data"
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                </Box>
                
                <form onSubmit={handleSubmit}>
                  <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <ScienceIcon />}
                    disabled={!file || loading}
                    sx={{ py: 1.5 }}
                  >
                    {loading ? 'Analyzing...' : 'Analyze Gut Health'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ height: '100%' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
                  <ScienceIcon sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    How It Works
                  </Typography>
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ maxWidth: 500 }}>
                    Our advanced AI analyzes your gut microbiome data to assess your overall gut health.
                    Based on the analysis, we provide personalized recommendations to improve your gut health,
                    which can lead to better digestion, immunity, and even glucose response to meals.
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      
      {loading && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Analyzing your microbiome data...
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default GutHealthAnalyzer; 