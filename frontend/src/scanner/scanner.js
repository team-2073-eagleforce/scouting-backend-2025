/**
 * QR Code Scanner Module - No Caching Version
 * Handles QR code scanning with immediate validation and processing
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
    this.pendingScans = new Set(); // Track pending scans to prevent duplicates
    
    this.init();
  }

  /**
   * Validate scan data before sending
   */
  validateScanData(scanData) {
    const errors = [];
    
    // Required fields
    const required = ['teamNumber', 'matchNumber', 'name', 'comp_code'];
    for (const field of required) {
      if (!scanData[field] || String(scanData[field]).trim() === '') {
        errors.push(`Missing ${field}`);
      }
    }
    
    // Validate team number
    const teamNum = parseInt(scanData.teamNumber);
    if (isNaN(teamNum) || teamNum <= 0 || teamNum > 99999) {
      errors.push('Invalid team number');
    }
    
    // Validate match number
    const matchNum = parseInt(scanData.matchNumber);
    if (isNaN(matchNum) || matchNum <= 0 || matchNum > 999) {
      errors.push('Invalid match number');
    }
    
    // Validate scout name
    const name = String(scanData.name).trim();
    if (name.length < 2 || name.length > 32) {
      errors.push('Scout name must be 2-32 characters');
    }
    
    return errors;
  }

  /**
   * Show validation error dialog
   */
  async showValidationDialog(errors, scanData) {
    const message = `Scan validation failed:\n${errors.join('\n')}\n\nOptions:\n1. Skip this scan\n2. Edit data manually`;
    
    if (confirm(message + '\n\nClick OK to edit manually, Cancel to skip')) {
      return this.showEditDialog(scanData);
    }
    return null;
  }

  /**
   * Show manual edit dialog
   */
  showEditDialog(scanData) {
    const teamNumber = prompt('Team Number:', scanData.teamNumber || '');
    if (teamNumber === null) return null;
    
    const matchNumber = prompt('Match Number:', scanData.matchNumber || '');
    if (matchNumber === null) return null;
    
    const name = prompt('Scout Name:', scanData.name || '');
    if (name === null) return null;
    
    const comp_code = prompt('Competition Code:', scanData.comp_code || '');
    if (comp_code === null) return null;
    
    return {
      ...scanData,
      teamNumber: teamNumber.trim(),
      matchNumber: matchNumber.trim(),
      name: name.trim(),
      comp_code: comp_code.trim()
    };
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
   */
  async loadQrScanner() {
    try {
      if (typeof QrScanner !== 'undefined') {
        return QrScanner;
      }
      
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
   * Handle scan result with validation
   */
  async handleScanResult(result) {
    const data = result.data;
    
    if (data === this.prevResult || this.pendingScans.has(data)) {
      return;
    }

    this.prevResult = data;
    this.pendingScans.add(data);
    
    try {
      const scanData = JSON.parse(data);
      const errors = this.validateScanData(scanData);
      
      let finalData = scanData;
      if (errors.length > 0) {
        this.showError(`Validation errors: ${errors.join(', ')}`);
        finalData = await this.showValidationDialog(errors, scanData);
        
        if (!finalData) {
          this.showMessage('Scan skipped', 'orange');
          return;
        }
        
        // Re-validate edited data
        const newErrors = this.validateScanData(finalData);
        if (newErrors.length > 0) {
          this.showError(`Still invalid: ${newErrors.join(', ')}`);
          return;
        }
      }
      
      await this.sendToServer(finalData);
      this.showMessage('Scan successful!', 'green');
      triggerHapticFeedback();
      
    } catch (error) {
      console.error('Failed to process scan:', error);
      this.showError('Invalid QR code format');
    } finally {
      this.pendingScans.delete(data);
    }
  }

  /**
   * Display message in UI
   */
  showMessage(message, color = 'inherit') {
    if (!this.resultDisplay) return;

    this.resultDisplay.textContent = message;
    this.resultDisplay.style.color = color;
    
    clearTimeout(this.resultDisplay.highlightTimeout);
    this.resultDisplay.highlightTimeout = setTimeout(() => {
      this.resultDisplay.style.color = 'inherit';
    }, 3000);
  }

  /**
   * Show error message
   */
  showError(message) {
    this.showMessage(message, 'red');
  }

  /**
   * Send validated data to server
   */
  async sendToServer(data) {
    try {
      const response = await postJSON('/scanner/', data);
      console.log('Server Response:', response);
      return response;
    } catch (error) {
      if (error.message.includes('Validation failed')) {
        this.showError('Server rejected data - validation failed');
      } else {
        this.showError('Server error - please try again');
      }
      throw error;
    }
  }

  /**
   * Setup event listeners
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
   * Populate camera options
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

    addEventListener(cameraSelect, 'change', (event) => {
      if (this.scanner) {
        this.scanner.setCamera(event.target.value);
      }
    });
  }

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

  stop() {
    if (this.scanner) {
      this.scanner.stop();
    }
  }

  destroy() {
    if (this.scanner) {
      this.scanner.stop();
      this.scanner.destroy();
      this.scanner = null;
    }
    this.isInitialized = false;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const scanner = new QRCodeScanner();
  
  if (process.env.NODE_ENV === 'development') {
    window.qrScanner = scanner;
  }
});

export default QRCodeScanner;