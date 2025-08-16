/**
 * Shared DOM utilities and helper functions
 */

/**
 * Safely get element by ID with error handling
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} Element or null if not found
 */
export function getElementById(id) {
  const element = document.getElementById(id);
  if (!element) {
    console.warn(`Element with ID '${id}' not found`);
  }
  return element;
}

/**
 * Safely query selector with error handling
 * @param {string} selector - CSS selector
 * @param {HTMLElement} context - Context element (default: document)
 * @returns {HTMLElement|null} Element or null if not found
 */
export function querySelector(selector, context = document) {
  try {
    return context.querySelector(selector);
  } catch (error) {
    console.error(`Invalid selector '${selector}':`, error);
    return null;
  }
}

/**
 * Safely query all selectors with error handling
 * @param {string} selector - CSS selector
 * @param {HTMLElement} context - Context element (default: document)
 * @returns {NodeList} NodeList (empty if error)
 */
export function querySelectorAll(selector, context = document) {
  try {
    return context.querySelectorAll(selector);
  } catch (error) {
    console.error(`Invalid selector '${selector}':`, error);
    return document.createDocumentFragment().querySelectorAll(selector);
  }
}

/**
 * Add event listener with error handling
 * @param {HTMLElement} element - Target element
 * @param {string} event - Event type
 * @param {Function} handler - Event handler
 * @param {Object} options - Event options
 */
export function addEventListener(element, event, handler, options = {}) {
  if (!element) {
    console.warn('Cannot add event listener to null element');
    return;
  }
  
  if (typeof handler !== 'function') {
    console.warn('Event handler must be a function');
    return;
  }
  
  try {
    element.addEventListener(event, handler, options);
  } catch (error) {
    console.error(`Failed to add ${event} listener:`, error);
  }
}

/**
 * Create element with attributes and content
 * @param {string} tagName - HTML tag name
 * @param {Object} attributes - Element attributes
 * @param {string|HTMLElement} content - Element content
 * @returns {HTMLElement} Created element
 */
export function createElement(tagName, attributes = {}, content = '') {
  const element = document.createElement(tagName);
  
  // Set attributes
  Object.entries(attributes).forEach(([key, value]) => {
    if (key === 'className') {
      element.className = value;
    } else if (key === 'dataset') {
      Object.entries(value).forEach(([dataKey, dataValue]) => {
        element.dataset[dataKey] = dataValue;
      });
    } else {
      element.setAttribute(key, value);
    }
  });
  
  // Set content
  if (typeof content === 'string') {
    element.textContent = content;
  } else if (content instanceof HTMLElement) {
    element.appendChild(content);
  }
  
  return element;
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - Execute immediately
 * @returns {Function} Debounced function
 */
export function debounce(func, wait, immediate = false) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func.apply(this, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(this, args);
  };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}