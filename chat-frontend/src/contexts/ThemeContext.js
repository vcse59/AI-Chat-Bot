import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Initialize theme from localStorage or default to 'dark'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('app-theme');
    return savedTheme || 'dark';
  });
  const [isLoading, setIsLoading] = useState(false);

  // Fetch theme from server when user is authenticated
  const fetchThemeFromServer = useCallback(async () => {
    if (authService.isAuthenticated()) {
      setIsLoading(true);
      try {
        const response = await authService.getThemePreference();
        if (response && response.theme_preference) {
          setTheme(response.theme_preference);
          localStorage.setItem('app-theme', response.theme_preference);
        }
      } catch (error) {
        console.error('Failed to fetch theme preference:', error);
        // Fall back to localStorage theme
      } finally {
        setIsLoading(false);
      }
    }
  }, []);

  // Apply theme class to document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  // Fetch theme from server on mount if authenticated
  useEffect(() => {
    fetchThemeFromServer();
  }, [fetchThemeFromServer]);

  const toggleTheme = async () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Save to server if authenticated
    if (authService.isAuthenticated()) {
      try {
        await authService.updateThemePreference(newTheme);
      } catch (error) {
        console.error('Failed to save theme preference:', error);
        // Theme is already updated locally, just log the error
      }
    }
  };

  const setThemeWithSync = async (newTheme) => {
    setTheme(newTheme);
    
    // Save to server if authenticated
    if (authService.isAuthenticated()) {
      try {
        await authService.updateThemePreference(newTheme);
      } catch (error) {
        console.error('Failed to save theme preference:', error);
      }
    }
  };

  const value = {
    theme,
    setTheme: setThemeWithSync,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    isLoading,
    refreshTheme: fetchThemeFromServer,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
