/**
 * Main entry point for the scouting backend frontend
 * This file is used by webpack to bundle shared dependencies
 */

// Import shared utilities to make them available
import '@shared/api';
import '@shared/utils';

// Global styles (if any)
// import './styles/main.css';

console.log('Scouting Backend Frontend initialized');

// Make development utilities available globally in development
if (process.env.NODE_ENV === 'development') {
  window.scoutingDebug = {
    version: '1.0.0',
    mode: process.env.NODE_ENV,
  };
}