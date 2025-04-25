import React, { createContext, useState, useContext } from 'react';

const AlertContext = createContext();

export const useAlert = () => useContext(AlertContext);

export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);

  // Add a new alert
  const addAlert = (message, type = 'info', timeout = 5000) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newAlert = {
      id,
      message,
      type,
    };
    
    setAlerts((prev) => [...prev, newAlert]);
    
    // Auto dismiss after timeout
    if (timeout) {
      setTimeout(() => {
        removeAlert(id);
      }, timeout);
    }
    
    return id;
  };

  // Remove an alert by ID
  const removeAlert = (id) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== id));
  };

  // Convenience methods for different alert types
  const success = (message, timeout) => addAlert(message, 'success', timeout);
  const error = (message, timeout) => addAlert(message, 'error', timeout);
  const warning = (message, timeout) => addAlert(message, 'warning', timeout);
  const info = (message, timeout) => addAlert(message, 'info', timeout);

  const value = {
    alerts,
    addAlert,
    removeAlert,
    success,
    error,
    warning,
    info,
  };

  return <AlertContext.Provider value={value}>{children}</AlertContext.Provider>;
}; 