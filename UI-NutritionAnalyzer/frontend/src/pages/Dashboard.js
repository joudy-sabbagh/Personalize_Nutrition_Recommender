import React, { useState } from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Button, 
  Avatar,
  Paper,
  IconButton,
  CardActions,
  Divider
} from '@mui/material';
import { 
  ArrowForward, 
  RestaurantMenu, 
  Timeline, 
  Science,
  QueryStats,
  ManageAccounts,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Mock data for demonstration
const mockRecentMeals = [
  { 
    id: 1, 
    name: 'Breakfast Oatmeal', 
    date: '2023-04-15 08:30', 
    glucoseSpike: 12, 
    category: 'breakfast',
    nutrients: { carbs: 35, protein: 12, fat: 5 }
  },
  { 
    id: 2, 
    name: 'Grilled Chicken Salad', 
    date: '2023-04-14 13:15', 
    glucoseSpike: 8, 
    category: 'lunch',
    nutrients: { carbs: 20, protein: 30, fat: 15 }
  },
  { 
    id: 3, 
    name: 'Salmon with Vegetables', 
    date: '2023-04-14 19:00', 
    glucoseSpike: 5, 
    category: 'dinner',
    nutrients: { carbs: 15, protein: 28, fat: 22 }
  }
];

const mockWeeklyStats = {
  avgGlucoseSpike: 8.5,
  mealCount: 21,
  improvement: 12,
  topCategory: 'lunch'
};

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [showAllMeals, setShowAllMeals] = useState(false);
  
  const displayedMeals = showAllMeals ? mockRecentMeals : mockRecentMeals.slice(0, 2);
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {isAuthenticated ? `Welcome back, ${user.name}!` : 'Welcome to NutritionIQ!'}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {isAuthenticated 
            ? 'Track your meals, monitor glucose responses, and get personalized recommendations.'
            : 'Sign in to track your nutrition and get personalized insights.'}
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', padding: 3 }}>
                  <Avatar
                    sx={{
                      backgroundColor: 'primary.main',
                      width: 56,
                      height: 56,
                      margin: '0 auto 16px',
                    }}
                  >
                    <RestaurantMenu fontSize="large" />
                  </Avatar>
                  <Typography variant="h6" component="div" gutterBottom>
                    Analyze Meal
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Upload a meal photo to analyze nutrients
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    component={RouterLink}
                    to="/meal-analyzer"
                    endIcon={<ArrowForward />}
                    fullWidth
                  >
                    Analyze
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', padding: 3 }}>
                  <Avatar
                    sx={{
                      backgroundColor: 'secondary.main',
                      width: 56,
                      height: 56,
                      margin: '0 auto 16px',
                    }}
                  >
                    <Timeline fontSize="large" />
                  </Avatar>
                  <Typography variant="h6" component="div" gutterBottom>
                    Predict Glucose
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Predict glucose response to a meal
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    component={RouterLink}
                    to="/glucose-predictor"
                    endIcon={<ArrowForward />}
                    fullWidth
                    color="secondary"
                  >
                    Predict
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', padding: 3 }}>
                  <Avatar
                    sx={{
                      backgroundColor: 'success.main',
                      width: 56,
                      height: 56,
                      margin: '0 auto 16px',
                    }}
                  >
                    <Science fontSize="large" />
                  </Avatar>
                  <Typography variant="h6" component="div" gutterBottom>
                    Gut Health
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Analyze your microbiome data
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    component={RouterLink}
                    to="/gut-health"
                    endIcon={<ArrowForward />}
                    fullWidth
                    color="success"
                  >
                    Analyze
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', padding: 3 }}>
                  <Avatar
                    sx={{
                      backgroundColor: 'info.main',
                      width: 56,
                      height: 56,
                      margin: '0 auto 16px',
                    }}
                  >
                    <ManageAccounts fontSize="large" />
                  </Avatar>
                  <Typography variant="h6" component="div" gutterBottom>
                    Your Profile
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Manage your personal information
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    component={RouterLink}
                    to="/profile"
                    endIcon={<ArrowForward />}
                    fullWidth
                    color="info"
                  >
                    View Profile
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Weekly Stats */}
        {isAuthenticated && (
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Weekly Stats
            </Typography>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                borderRadius: 2,
                border: 1,
                borderColor: 'divider',
              }}
            >
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Glucose Spike
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {mockWeeklyStats.avgGlucoseSpike}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Meals Logged
                  </Typography>
                  <Typography variant="h4" sx={{ mt: 1 }}>
                    {mockWeeklyStats.mealCount}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                      Improvement
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', color: 'success.main' }}>
                      <ArrowUpward fontSize="small" />
                      <Typography variant="body2" fontWeight="bold">
                        {mockWeeklyStats.improvement}%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Best Category
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" sx={{ textTransform: 'capitalize' }}>
                    {mockWeeklyStats.topCategory}
                  </Typography>
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 2 }} />
              
              <Button
                fullWidth
                endIcon={<QueryStats />}
                size="small"
                component={RouterLink}
                to="/insights"
              >
                View Detailed Insights
              </Button>
            </Paper>
          </Grid>
        )}
        
        {/* Recent Meals */}
        {isAuthenticated && (
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Recent Meals
              </Typography>
              <Button 
                size="small" 
                onClick={() => setShowAllMeals(!showAllMeals)}
              >
                {showAllMeals ? 'Show Less' : 'View All'}
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {displayedMeals.map((meal) => (
                <Grid item xs={12} key={meal.id}>
                  <Card>
                    <CardContent>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={8}>
                          <Typography variant="h6" component="div">
                            {meal.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {new Date(meal.date).toLocaleString()}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Carbs
                              </Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {meal.nutrients.carbs}g
                              </Typography>
                            </Box>
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Protein
                              </Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {meal.nutrients.protein}g
                              </Typography>
                            </Box>
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                Fat
                              </Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {meal.nutrients.fat}g
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}>
                            <Box textAlign="center">
                              <Typography variant="caption" color="text.secondary">
                                Glucose Response
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                {meal.glucoseSpike <= 10 ? (
                                  <ArrowDownward color="success" />
                                ) : (
                                  <ArrowUpward color="error" />
                                )}
                                <Typography 
                                  variant="h6" 
                                  color={meal.glucoseSpike <= 10 ? 'success.main' : 'error.main'}
                                >
                                  {meal.glucoseSpike} mg/dL
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                    <CardActions>
                      <Button size="small">View Details</Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default Dashboard; 