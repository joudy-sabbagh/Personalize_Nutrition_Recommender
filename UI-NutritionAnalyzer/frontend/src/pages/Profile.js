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
  Avatar,
  Divider,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useAlert } from '../context/AlertContext';

const Profile = () => {
  const { user } = useAuth();
  const { success } = useAlert();
  const [activeTab, setActiveTab] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    age: '',
    height: '',
    weight: '',
    dietaryPreferences: '',
    allergies: ''
  });
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSaveProfile = () => {
    // In a real app, you would save the user profile data to your backend here
    setIsEditing(false);
    success('Profile updated successfully');
  };
  
  const renderPersonalInfoTab = () => {
    return (
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Button
            startIcon={isEditing ? <SaveIcon /> : <EditIcon />}
            onClick={isEditing ? handleSaveProfile : () => setIsEditing(true)}
            variant={isEditing ? "contained" : "outlined"}
            color="primary"
          >
            {isEditing ? 'Save Changes' : 'Edit Profile'}
          </Button>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Phone Number"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Age"
              name="age"
              type="number"
              value={formData.age}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Height (cm)"
              name="height"
              type="number"
              value={formData.height}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Weight (kg)"
              name="weight"
              type="number"
              value={formData.weight}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Dietary Preferences"
              name="dietaryPreferences"
              value={formData.dietaryPreferences}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
              placeholder="E.g., vegetarian, low carb, high protein"
            />
            <TextField
              fullWidth
              label="Food Allergies"
              name="allergies"
              value={formData.allergies}
              onChange={handleInputChange}
              disabled={!isEditing}
              margin="normal"
              placeholder="E.g., nuts, dairy, gluten"
            />
          </Grid>
        </Grid>
      </Box>
    );
  };
  
  const renderSettingsTab = () => {
    return (
      <Box sx={{ mt: 3 }}>
        <List>
          <ListItem>
            <ListItemIcon>
              <NotificationsIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Email Notifications" 
              secondary="Receive updates about your meal analysis and glucose predictions"
            />
            <FormControlLabel 
              control={<Switch defaultChecked />} 
              label=""
            />
          </ListItem>
          <Divider />
          <ListItem>
            <ListItemIcon>
              <SecurityIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Data Privacy" 
              secondary="Share anonymized data to improve our AI models"
            />
            <FormControlLabel 
              control={<Switch defaultChecked />} 
              label=""
            />
          </ListItem>
          <Divider />
          <ListItem>
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Units of Measurement" 
              secondary="Choose between metric (g, cm, kg) and imperial (oz, in, lb) units"
            />
            <Box sx={{ minWidth: 120 }}>
              <FormControlLabel 
                control={<Switch defaultChecked />} 
                label="Metric"
              />
            </Box>
          </ListItem>
        </List>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" color="primary">
            Save Settings
          </Button>
        </Box>
      </Box>
    );
  };
  
  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderPersonalInfoTab();
      case 1:
        return renderSettingsTab();
      default:
        return renderPersonalInfoTab();
    }
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Profile
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Avatar
                src={user?.profilePicture || ''}
                alt={user?.name || 'User'}
                sx={{ width: 120, height: 120, margin: '0 auto 16px', border: '4px solid #f5f5f5' }}
              />
              <Typography variant="h5" gutterBottom>
                {user?.name || 'Guest User'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {user?.email || 'guest@example.com'}
              </Typography>
              
              <Divider sx={{ my: 3 }} />
              
              <Box sx={{ textAlign: 'left' }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Account Summary
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Meals Analyzed
                    </Typography>
                    <Typography variant="h6">
                      24
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Member Since
                    </Typography>
                    <Typography variant="h6">
                      Apr 2023
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
              
              <Button 
                variant="outlined" 
                fullWidth 
                color="primary"
                startIcon={<EditIcon />}
                sx={{ mt: 3 }}
              >
                Change Profile Photo
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs 
                  value={activeTab} 
                  onChange={handleTabChange} 
                  aria-label="profile tabs"
                >
                  <Tab 
                    label="Personal Information" 
                    icon={<PersonIcon />} 
                    iconPosition="start"
                  />
                  <Tab 
                    label="Settings" 
                    icon={<SettingsIcon />} 
                    iconPosition="start"
                  />
                </Tabs>
              </Box>
              
              {renderTabContent()}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile; 