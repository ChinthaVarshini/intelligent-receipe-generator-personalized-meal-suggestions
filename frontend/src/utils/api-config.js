/**
 * API Configuration
 * This utility handles secure API communication.
 * Since the frontend is served from the same domain as the backend,
 * we don't need to expose API keys in the frontend code.
 */

// Get headers for API requests
export const getApiHeaders = (additionalHeaders = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...additionalHeaders
  };
  
  // Only add Authorization header if we have a token
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Get FormData headers for multipart requests
export const getFormDataHeaders = (additionalHeaders = {}) => {
  const headers = {
    ...additionalHeaders
  };
  
  // Only add Authorization header if we have a token
  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Don't set Content-Type for FormData - browser sets it with boundary
  return headers;
};

// Safe fetch wrapper
export const secureFetch = async (url, options = {}) => {
  const finalOptions = {
    ...options,
    headers: options.headers || getApiHeaders()
  };
  
  return fetch(url, finalOptions);
};
