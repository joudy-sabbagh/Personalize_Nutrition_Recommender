import React, { useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  IconButton, 
  Avatar, 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Divider,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { 
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  RestaurantMenu as RestaurantIcon,
  Timeline as TimelineIcon,
  Science as ScienceIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  
  const openUserMenu = Boolean(anchorEl);
  
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const handleUserMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };
  
  const navItems = [
    { text: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { text: 'Meal Analyzer', path: '/meal-analyzer', icon: <RestaurantIcon /> },
    { text: 'Glucose Predictor', path: '/glucose-predictor', icon: <TimelineIcon /> },
    { text: 'Gut Health', path: '/gut-health', icon: <ScienceIcon /> },
  ];
  
  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center', width: 250 }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        NutritionIQ
      </Typography>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem 
            button 
            component={RouterLink} 
            to={item.path} 
            key={item.text}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
  
  return (
    <>
      <AppBar position="static" elevation={0} color="default" sx={{ backgroundColor: 'white' }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography 
            variant="h6" 
            component={RouterLink} 
            to="/" 
            sx={{ 
              flexGrow: 1, 
              textDecoration: 'none', 
              color: 'primary.main',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            NutritionIQ
          </Typography>
          
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {navItems.map((item) => (
                <Button
                  key={item.text}
                  component={RouterLink}
                  to={item.path}
                  color={location.pathname === item.path ? 'primary' : 'inherit'}
                  sx={{ 
                    mx: 1,
                    fontWeight: location.pathname === item.path ? 600 : 400,
                    borderBottom: location.pathname === item.path ? '2px solid' : 'none',
                    borderRadius: 0,
                    paddingBottom: '4px'
                  }}
                  startIcon={item.icon}
                >
                  {item.text}
                </Button>
              ))}
            </Box>
          )}
          
          {isAuthenticated ? (
            <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
              <IconButton onClick={handleUserMenuClick} size="small">
                <Avatar 
                  alt={user.name}
                  src={user.profilePicture}
                  sx={{ width: 40, height: 40 }}
                />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={openUserMenu}
                onClose={handleUserMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem component={RouterLink} to="/profile">
                  <ListItemIcon>
                    <PersonIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Profile</ListItemText>
                </MenuItem>
                <MenuItem>
                  <ListItemIcon>
                    <SettingsIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Settings</ListItemText>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Logout</ListItemText>
                </MenuItem>
              </Menu>
            </Box>
          ) : (
            <Box>
              <Button 
                color="inherit" 
                component={RouterLink} 
                to="/login"
                sx={{ mx: 1 }}
              >
                Login
              </Button>
              <Button 
                variant="contained" 
                color="primary" 
                component={RouterLink} 
                to="/register"
              >
                Register
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navbar; 