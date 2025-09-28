/**
 * QR Code Scanner Module
 * Handles QR code scanning functionality with camera integration
 */

import { postJSON, triggerHapticFeedback } from '@shared/api';
import { getElementById, addEventListener } from '@shared/utils';

class QRCodeScanner {
  constructor() {
    this.video = null;
    this.resultDisplay = null;
    this.scanner = null;
    this.prevResult = '';
    this.isInitialized = false;
    
    this.init();
  }

  /**
   * Initialize the scanner
   */
  async init() {
    try {
      this.video = getElementById('qr-video');
      this.resultDisplay = getElementById('cam-qr-result');
      
      if (!this.video || !this.resultDisplay) {
        console.error('Required elements not found for QR scanner');
        return;
      }

      // Dynamically import QrScanner to handle the external library
      const QrScanner = await this.loadQrScanner();
      
      if (!QrScanner) {
        console.error('QrScanner library not available');
        return;
      }

      this.scanner = new QrScanner(
        this.video,
        result => this.handleScanResult(result),
        {
          highlightScanRegion: true,
          highlightCodeOutline: true,
        },
      );

      this.setupEventListeners();
      await this.startScanner();
      
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize QR scanner:', error);
    }
  }

  /**
   * Load QrScanner library
   * @returns {Promise<Object>} QrScanner class
   */
  async loadQrScanner() {
    try {
      // In production, this would be bundled or loaded from static files
      if (typeof QrScanner !== 'undefined') {
        return QrScanner;
      }
      
      // Fallback: load from static files
      const script = document.createElement('script');
      script.src = '/static/scanner/qr-scanner.min.js';
      document.head.appendChild(script);
      
      return new Promise((resolve, reject) => {
        script.onload = () => {
          if (typeof QrScanner !== 'undefined') {
            resolve(QrScanner);
          } else {
            reject(new Error('QrScanner not loaded'));
          }
        };
        script.onerror = () => reject(new Error('Failed to load QrScanner'));
      });
    } catch (error) {
      console.error('Error loading QrScanner:', error);
      return null;
    }
  }

  /**
   * Handle scan result
   * @param {Object} result - Scan result from QrScanner
   */
  async handleScanResult(result) {
    const data = result.data;
    
    if (data === this.prevResult || data.includes('error')) {
      return;
    }

    this.prevResult = data;
    this.displayResult(data);
    
    try {
      await this.sendToServer(data);
      triggerHapticFeedback();
    } catch (error) {
      console.error('Failed to send scan result to server:', error);
      this.showError('Failed to process scan result');
    }
  }

  /**
   * Display scan result in UI
   * @param {string} data - Scanned data
   */
  displayResult(data) {
    if (!this.resultDisplay) return;

    console.log('Scanned Data:', data);
    this.resultDisplay.textContent = data;
    this.resultDisplay.style.color = 'teal';
    
    // Clear previous timeout
    clearTimeout(this.resultDisplay.highlightTimeout);
    
    // Reset color after animation
    this.resultDisplay.highlightTimeout = setTimeout(() => {
      this.resultDisplay.style.color = 'inherit';
    }, 100);
  }

  /**
   * Send scanned data to Django backend
   * @param {string} data - Scanned data
   */
  async sendToServer(data) {
    try {
      const response = await postJSON('/scanner/', { qr_data: data });
      console.log('Server Response:', response);
      return response;
    } catch (error) {
      console.error('Error sending to server:', error);
      throw error;
    }
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    if (this.resultDisplay) {
      this.resultDisplay.textContent = message;
      this.resultDisplay.style.color = 'red';
    }
  }

  /**
   * Setup event listeners for scanner controls
   */
  setupEventListeners() {
    const startButton = getElementById('start-button');
    const stopButton = getElementById('stop-button');

    if (startButton) {
      addEventListener(startButton, 'click', () => this.start());
    }

    if (stopButton) {
      addEventListener(stopButton, 'click', () => this.stop());
    }
  }

  /**
   * Start the scanner
   */
  async startScanner() {
    if (!this.scanner) return;

    try {
      await this.scanner.start();
      
      // List available cameras
      if (typeof QrScanner !== 'undefined') {
        const cameras = await QrScanner.listCameras(true);
        this.populateCameraOptions(cameras);
      }
    } catch (error) {
      console.error('Failed to start scanner:', error);
      this.showError('Failed to start camera');
    }
  }

  /**
   * Populate camera selection options
   * @param {Array} cameras - Available cameras
   */
  populateCameraOptions(cameras) {
    const cameraSelect = getElementById('camera-select');
    if (!cameraSelect) return;

    cameras.forEach(camera => {
      const option = document.createElement('option');
      option.value = camera.id;
      option.text = camera.label;
      cameraSelect.appendChild(option);
    });

    // Add change listener for camera selection
    addEventListener(cameraSelect, 'change', (event) => {
      if (this.scanner) {
        this.scanner.setCamera(event.target.value);
      }
    });
  }

  /**
   * Start scanning (public method)
   */
  async start() {
    if (this.scanner) {
      try {
        await this.scanner.start();
      } catch (error) {
        console.error('Failed to start scanner:', error);
        this.showError('Failed to start scanning');
      }
    }
  }

  /**
   * Stop scanning (public method)
   */
  stop() {
    if (this.scanner) {
      this.scanner.stop();
    }
  }

  /**
   * Destroy scanner instance
   */
  destroy() {
    if (this.scanner) {
      this.scanner.stop();
      this.scanner.destroy();
      this.scanner = null;
    }
    this.isInitialized = false;
  }
}

// Initialize scanner when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const scanner = new QRCodeScanner();
  
  // Make scanner available globally for debugging
  if (process.env.NODE_ENV === 'development') {
    window.qrScanner = scanner;
  }
});

export default QRCodeScanner;