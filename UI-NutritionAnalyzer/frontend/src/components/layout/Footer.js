import React from 'react';
import { Box, Typography, Container, Link, IconButton, Divider } from '@mui/material';
import { GitHub, LinkedIn, Twitter } from '@mui/icons-material';

const Footer = () => {
  return (
    <Box 
      component="footer" 
      sx={{ 
        py: 3, 
        px: 2, 
        mt: 'auto',
        backgroundColor: (theme) => theme.palette.grey[100]
      }}
    >
      <Container maxWidth="lg">
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Box sx={{ mb: { xs: 2, md: 0 } }}>
            <Typography variant="h6" color="primary" fontWeight="bold">
              NutritionIQ
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Personalized nutrition recommendations powered by AI
            </Typography>
          </Box>
          
          <Box 
            sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' },
              alignItems: 'center'
            }}
          >
            <Box sx={{ mx: { sm: 3 }, mb: { xs: 2, sm: 0 } }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Quick Links
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Link href="#" color="inherit" underline="hover">About</Link>
                <Link href="#" color="inherit" underline="hover">Contact</Link>
                <Link href="#" color="inherit" underline="hover">Privacy</Link>
              </Box>
            </Box>
            
            <Box>
              <IconButton color="primary" aria-label="github" size="small">
                <GitHub />
              </IconButton>
              <IconButton color="primary" aria-label="linkedin" size="small">
                <LinkedIn />
              </IconButton>
              <IconButton color="primary" aria-label="twitter" size="small">
                <Twitter />
              </IconButton>
            </Box>
          </Box>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="body2" color="text.secondary" align="center">
          © {new Date().getFullYear()} NutritionIQ. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 