/**
 * Team Picklist Management Module
 * Handles drag-and-drop team selection for match strategy
 */

import { postJSON, triggerHapticFeedback, getCookie } from '@shared/api';
import { getElementById, querySelector, addEventListener, createElement, debounce } from '@shared/utils';

class TeamPicklist {
  constructor(compCode) {
    this.compCode = compCode;
    this.draggedItem = null;
    this.saveTimeout = null;
    this.lastUpdateTime = 0;
    this.lastTimestamp = 0;
    this.isFetching = false;
    
    // Configuration
    this.config = {
      inactivityTimeout: 3000, // 3 seconds of inactivity before auto-save
      fetchUpdateInterval: 5000, // Fetch updates every 5 seconds
      listIds: ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'],
    };

    // UI Elements
    this.elements = {
      saveButton: null,
      statusDiv: null,
      statusMessage: null,
      lists: {},
    };

    this.init();
  }

  /**
   * Initialize the picklist system
   */
  init() {
    this.initializeElements();
    this.setupEventListeners();
    this.startPeriodicUpdates();
    this.setupAutoSave();
  }

  /**
   * Initialize DOM elements
   */
  initializeElements() {
    this.elements.saveButton = querySelector('.save-button');
    this.elements.statusDiv = querySelector('.save-status');
    this.elements.statusMessage = querySelector('.status-message');

    // Initialize list elements
    this.config.listIds.forEach(listId => {
      this.elements.lists[listId] = getElementById(listId);
    });

    // Check if required elements exist
    if (!this.elements.saveButton) {
      console.warn('Save button not found');
    }
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Save button
    if (this.elements.saveButton) {
      addEventListener(this.elements.saveButton, 'click', () => this.saveToDB());
    }

    // Drag and drop for all lists
    Object.values(this.elements.lists).forEach(list => {
      if (list) {
        this.setupListEventListeners(list);
      }
    });

    // Global drag events
    addEventListener(document, 'dragover', e => e.preventDefault());
    addEventListener(document, 'drop', e => this.handleGlobalDrop(e));
  }

  /**
   * Setup event listeners for a specific list
   * @param {HTMLElement} list - List element
   */
  setupListEventListeners(list) {
    addEventListener(list, 'dragover', e => this.onDragOver(e));
    addEventListener(list, 'drop', e => this.onDrop(e));
  }

  /**
   * Get team data from all lists
   * @returns {Array} Array of team arrays for each list
   */
  getTeamData() {
    return this.config.listIds.map(listId => {
      const list = this.elements.lists[listId];
      if (!list) return [];
      
      return Array.from(list.children)
        .map(item => parseInt(item.id))
        .filter(id => !isNaN(id));
    });
  }

  /**
   * Save data temporarily (frequent updates)
   */
  async saveTemporary() {
    try {
      const data = this.getTeamData();
      const response = await fetch(`/strategy/picklist/submit/?comp=${this.compCode}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      this.lastTimestamp = result.timestamp;
      return result;
    } catch (error) {
      console.error('Error saving temporarily:', error);
      throw error;
    }
  }

  /**
   * Save data to database (infrequent updates)
   */
  async saveToDB() {
    if (!this.elements.saveButton) return;

    this.elements.saveButton.disabled = true;
    this.showStatus('Saving...', 'loading');

    try {
      const data = this.getTeamData();
      
      const response = await postJSON(
        `/strategy/picklist/submit/?comp=${this.compCode}&save_to_db=true`, 
        data
      );

      this.showStatus('Sent to database!', 'success');
      triggerHapticFeedback();

      // Reset UI after delay
      setTimeout(() => {
        this.hideStatus();
        this.elements.saveButton.disabled = false;
      }, 3000);

      return response;
    } catch (error) {
      console.error('Error saving to database:', error);
      this.showStatus('Error saving to database. Please try again.', 'error');
      this.elements.saveButton.disabled = false;

      setTimeout(() => {
        this.hideStatus();
      }, 5000);
      
      throw error;
    }
  }

  /**
   * Show status message
   * @param {string} message - Status message
   * @param {string} type - Status type (success, error, loading)
   */
  showStatus(message, type = 'info') {
    if (!this.elements.statusDiv || !this.elements.statusMessage) return;

    this.elements.statusMessage.textContent = message;
    this.elements.statusDiv.style.display = 'block';
    
    // Remove existing status classes
    this.elements.statusDiv.classList.remove('success', 'error', 'loading');
    this.elements.saveButton?.classList.remove('success');
    
    // Add new status class
    if (type === 'success') {
      this.elements.statusDiv.classList.add('success');
      this.elements.saveButton?.classList.add('success');
    } else if (type === 'error') {
      this.elements.statusDiv.classList.add('error');
    } else if (type === 'loading') {
      this.elements.statusDiv.classList.add('loading');
    }
  }

  /**
   * Hide status message
   */
  hideStatus() {
    if (this.elements.statusDiv) {
      this.elements.statusDiv.style.display = 'none';
    }
    this.elements.saveButton?.classList.remove('success');
  }

  /**
   * Reset the inactivity timer
   */
  resetInactivityTimer() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
    
    this.saveTimeout = setTimeout(() => {
      this.saveToDB(); // Auto-save to the database after inactivity
    }, this.config.inactivityTimeout);
  }

  /**
   * Create team element HTML
   * @param {number} team - Team number
   * @returns {HTMLElement} Team element
   */
  createTeamElement(team) {
    const li = createElement('li', {
      className: 'picklist_teams',
      draggable: 'true',
      id: team.toString(),
    });

    const p = createElement('p', {}, team.toString());
    const checkbox = createElement('input', { type: 'checkbox' });

    // Add event listeners
    addEventListener(li, 'dragstart', e => this.onDragStart(e));
    addEventListener(li, 'dragover', e => this.onDragOver(e));
    addEventListener(li, 'drop', e => this.onDrop(e));
    addEventListener(checkbox, 'change', e => this.onTeamChosen(e));

    li.appendChild(p);
    li.appendChild(checkbox);

    return li;
  }

  /**
   * Fetch updates from server with throttling
   */
  async fetchUpdates() {
    if (this.isFetching) return; // Prevent overlapping requests
    this.isFetching = true;

    try {
      const url = `/strategy/picklist/submit/?comp=${this.compCode}&timestamp=${this.lastTimestamp}&t=${Date.now()}`;
      const response = await fetch(url, {
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
        },
      });

      const result = await response.json();
      
      if (result.status === 'updated') {
        this.lastTimestamp = result.timestamp;
        this.updateLists(result.data);
      } else if (result.status === 'no_change') {
        this.lastTimestamp = result.timestamp;
      }
    } catch (error) {
      console.error('Error fetching updates:', error);
    } finally {
      this.isFetching = false;
    }
  }

  /**
   * Update lists with new data
   * @param {Array} data - Array of team arrays for each list
   */
  updateLists(data) {
    this.config.listIds.forEach((listId, index) => {
      const list = this.elements.lists[listId];
      if (!list) return;

      const currentTeams = Array.from(list.children).map(item => parseInt(item.id));
      const newTeams = data[index] || [];

      // Only update if there are actual changes and we're not currently dragging
      if (JSON.stringify(currentTeams) !== JSON.stringify(newTeams) && !this.draggedItem) {
        // Clear existing content
        list.innerHTML = '';
        
        // Add new teams
        newTeams.forEach(team => {
          const teamElement = this.createTeamElement(team);
          list.appendChild(teamElement);
        });
      }
    });
  }

  /**
   * Save with debouncing
   */
  save = debounce(() => {
    this.saveTemporary();
    this.resetInactivityTimer();
  }, 300);

  /**
   * Handle drag start
   * @param {DragEvent} event - Drag event
   */
  onDragStart(event) {
    this.draggedItem = event.target;
    event.dataTransfer.setData('team_number_id', event.target.id);
    event.dataTransfer.effectAllowed = 'move';
    this.draggedItem.classList.add('being-dragged');
    this.resetInactivityTimer();
  }

  /**
   * Handle drag over
   * @param {DragEvent} event - Drag event
   */
  onDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }

  /**
   * Handle drop
   * @param {DragEvent} event - Drop event
   */
  onDrop(event) {
    event.preventDefault();
    
    if (!this.draggedItem) return;

    const targetList = event.currentTarget;
    const afterElement = this.getDragAfterElement(targetList, event.clientY);

    if (afterElement == null) {
      targetList.appendChild(this.draggedItem);
    } else {
      targetList.insertBefore(this.draggedItem, afterElement);
    }

    this.draggedItem.classList.remove('being-dragged');
    this.draggedItem = null;
    
    this.save();
  }

  /**
   * Handle global drop (cleanup)
   * @param {DragEvent} event - Drop event
   */
  handleGlobalDrop(event) {
    if (this.draggedItem) {
      this.draggedItem.classList.remove('being-dragged');
      this.draggedItem = null;
    }
  }

  /**
   * Get the element after which the dragged item should be inserted
   * @param {HTMLElement} container - Container element
   * @param {number} y - Y coordinate
   * @returns {HTMLElement|null} Element or null
   */
  getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.picklist_teams:not(.being-dragged)')];
    
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }

  /**
   * Handle team chosen (checkbox)
   * @param {Event} event - Change event
   */
  onTeamChosen(event) {
    const checkbox = event.target;
    const teamElement = checkbox.closest('.picklist_teams');
    
    if (checkbox.checked) {
      teamElement.classList.add('chosen');
    } else {
      teamElement.classList.remove('chosen');
    }
    
    this.save();
  }

  /**
   * Start periodic updates
   */
  startPeriodicUpdates() {
    setInterval(() => {
      this.fetchUpdates();
    }, this.config.fetchUpdateInterval);
  }

  /**
   * Setup auto-save functionality
   */
  setupAutoSave() {
    // Auto-save on page unload
    addEventListener(window, 'beforeunload', () => {
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout);
        this.saveTemporary();
      }
    });
  }

  /**
   * Destroy the picklist instance
   */
  destroy() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
    
    // Remove event listeners would be handled by modern browsers on element removal
    this.draggedItem = null;
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Get competition code from global variable or data attribute
  const compCode = window.comp_code || document.body.dataset.compCode || '';
  
  if (!compCode) {
    console.error('Competition code not found');
    return;
  }

  const picklist = new TeamPicklist(compCode);
  
  // Make available globally for debugging
  if (process.env.NODE_ENV === 'development') {
    window.teamPicklist = picklist;
  }
});

export default TeamPicklist;