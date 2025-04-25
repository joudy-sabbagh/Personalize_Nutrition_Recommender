import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Layout Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import AlertList from './components/common/AlertList';

// Pages
import Dashboard from './pages/Dashboard';
import MealAnalyzer from './pages/MealAnalyzer';
import GlucosePredictor from './pages/GlucosePredictor';
import GutHealthAnalyzer from './pages/GutHealthAnalyzer';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

// Context Providers
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';

// Custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // Green - representing health/nutrition
      light: '#4CAF50',
      dark: '#1B5E20',
    },
    secondary: {
      main: '#1976D2', // Blue - representing data/analytics
      light: '#42A5F5',
      dark: '#0D47A1',
    },
    error: {
      main: '#D32F2F',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 500,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 30,
          padding: '8px 20px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.05)',
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AlertProvider>
          <Router>
            <div className="app-container">
              <Navbar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/meal-analyzer" element={<MealAnalyzer />} />
                  <Route path="/glucose-predictor" element={<GlucosePredictor />} />
                  <Route path="/gut-health" element={<GutHealthAnalyzer />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </main>
              <Footer />
              <AlertList />
            </div>
          </Router>
        </AlertProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
