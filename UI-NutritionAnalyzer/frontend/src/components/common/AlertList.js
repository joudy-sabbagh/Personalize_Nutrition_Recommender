import React from 'react';
import { Alert, Snackbar, Box } from '@mui/material';
import { useAlert } from '../../context/AlertContext';

const AlertList = () => {
  const alertContext = useAlert();
  const { removeAlert } = alertContext;
  const alerts = alertContext?.alerts || [];

  if (!alerts.length) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: (theme) => theme.spacing(2),
        right: (theme) => theme.spacing(2),
        zIndex: 2000,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
      }}
    >
      {alerts.map((alert) => (
        <Snackbar
          key={alert.id}
          open={true}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          onClose={() => removeAlert(alert.id)}
          autoHideDuration={6000}
          sx={{ position: 'relative', mt: 1 }}
        >
          <Alert
            onClose={() => removeAlert(alert.id)}
            severity={alert.type}
            variant="filled"
            sx={{ width: '100%', boxShadow: 3 }}
          >
            {alert.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default AlertList; 