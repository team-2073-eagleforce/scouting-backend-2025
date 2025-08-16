/**
 * Shared API utilities for making HTTP requests to the Django backend
 */

/**
 * Get CSRF token from Django cookies
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value
 */
export function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(`${name}=`)) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Make a JSON API request with CSRF protection
 * @param {string} url - Request URL
 * @param {Object} options - Request options
 * @returns {Promise<Response>} Fetch response
 */
export async function apiRequest(url, options = {}) {
  const defaultOptions = {
    method: 'GET',
    credentials: 'include',
    mode: 'same-origin',
    headers: {
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...options.headers,
    },
  };

  // Add CSRF token for non-GET requests
  if (options.method && options.method !== 'GET') {
    defaultOptions.headers['X-CSRFToken'] = getCookie('csrftoken');
  }

  // Add Content-Type for JSON requests
  if (options.body && typeof options.body === 'object') {
    defaultOptions.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const mergedOptions = { ...defaultOptions, ...options };
  
  try {
    const response = await fetch(url, mergedOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error('API Request failed:', error);
    throw error;
  }
}

/**
 * Post JSON data to the server
 * @param {string} url - Request URL
 * @param {Object} data - Data to send
 * @returns {Promise<Object>} Response data
 */
export async function postJSON(url, data) {
  const response = await apiRequest(url, {
    method: 'POST',
    body: data,
  });
  return response.json();
}

/**
 * Trigger haptic feedback if supported
 */
export function triggerHapticFeedback() {
  if (navigator.vibrate) {
    navigator.vibrate(50);
  }
}