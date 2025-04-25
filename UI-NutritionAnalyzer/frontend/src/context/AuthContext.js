import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Initialize auth state from localStorage on app load
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // Mock login function - would connect to backend in production
  const login = async (email, password) => {
    // Simulate API call
    setLoading(true);
    
    try {
      // In a real app, this would be an API call
      // For demo purposes, we'll simulate a successful login
      const userData = {
        id: '1',
        name: 'John Doe',
        email: email,
        profilePicture: 'https://randomuser.me/api/portraits/men/32.jpg',
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const register = async (name, email, password) => {
    setLoading(true);
    
    try {
      // In a real app, this would be an API call
      const userData = {
        id: '1',
        name: name,
        email: email,
        profilePicture: 'https://randomuser.me/api/portraits/men/32.jpg',
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 