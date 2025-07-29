import React from 'react';
import { Toaster } from 'react-hot-toast';

const ToastProvider: React.FC = () => {
  return (
    <Toaster
      position="bottom-center"
      reverseOrder={false}
      gutter={8}
      containerStyle={{
        bottom: 80, // Above mobile nav
      }}
      toastOptions={{
        duration: 5000,
        style: {
          background: 'var(--toast-bg)',
          color: 'var(--toast-text)',
          padding: 'var(--toast-padding)',
          borderRadius: 'var(--toast-radius)',
          fontSize: '14px',
          minWidth: '300px',
          maxWidth: '500px',
        },
        success: {
          iconTheme: {
            primary: '#10b981',
            secondary: '#ffffff',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#ffffff',
          },
        },
      }}
    />
  );
};

export default ToastProvider;