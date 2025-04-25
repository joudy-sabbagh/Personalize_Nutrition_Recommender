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
      setResults(response);
      success('Gut health analysis completed successfully!');
    } catch (err) {
      error(err.response?.data?.error || 'Failed to analyze microbiome data');
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;
    
    return (
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Your Gut Health Analysis
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Overall Gut Health Score
              </Typography>
              
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 3, 
                  textAlign: 'center',
                  backgroundColor: results.score > 70 ? '#e8f5e9' : results.score > 50 ? '#fff8e1' : '#ffebee'
                }}
              >
                <Typography variant="h2" color={results.score > 70 ? 'success.main' : results.score > 50 ? 'warning.main' : 'error.main'}>
                  {results.score}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  out of 100
                </Typography>
              </Paper>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="body1" fontWeight="medium">
                  {results.assessment || 'Your gut microbiome shows a moderate diversity profile. There is room for improvement in certain bacterial populations.'}
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Key Indicators
              </Typography>
              
              {results.indicators ? (
                results.indicators.map((indicator, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body1">
                        {indicator.name}
                      </Typography>
                      <Typography 
                        variant="body1" 
                        fontWeight="medium"
                        color={indicator.status === 'good' ? 'success.main' : indicator.status === 'fair' ? 'warning.main' : 'error.main'}
                      >
                        {indicator.status.charAt(0).toUpperCase() + indicator.status.slice(1)}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {indicator.description}
                    </Typography>
                    <Divider sx={{ mt: 1 }} />
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No specific indicators available
                </Typography>
              )}
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          
          {results.recommendations ? (
            <ul>
              {results.recommendations.map((rec, index) => (
                <li key={index}>
                  <Typography variant="body1" paragraph>
                    {rec}
                  </Typography>
                </li>
              ))}
            </ul>
          ) : (
            <Typography variant="body1" paragraph>
              Based on your gut microbiome profile, consider increasing your intake of diverse plant-based foods to enhance microbial diversity. Fermented foods like yogurt and sauerkraut may help improve beneficial bacteria levels.
            </Typography>
          )}
          
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
      
      <Grid container spacing={4}>
        {!results && (
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
        )}
        
        <Grid item xs={12} md={results ? 12 : 6}>
          {loading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
              <CircularProgress />
              <Typography variant="body1" sx={{ mt: 2 }}>
                Analyzing your microbiome data...
              </Typography>
            </Box>
          ) : (
            results ? renderResults() : (
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
            )
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default GutHealthAnalyzer; 