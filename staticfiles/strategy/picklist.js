// ================================
// Picklist JS (Fixed & Optimized)
// ================================

let draggedItem = null;
let saveTimeout = null;
// lastTimestamp is initialized from the server in the template
const INACTIVITY_TIMEOUT = 3000; // 3 seconds before auto-save
const FETCH_UPDATE_INTERVAL = 5000; // Fetch updates every 5 seconds
let isFetching = false; // To prevent overlapping fetch requests

// ----------------
// Utility Functions
// ----------------

// Get CSRF token (for Django POST requests)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Trigger haptic feedback if supported
function triggerHapticFeedback() {
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

// Sanitize team IDs for HTML
function sanitizeId(team) {
    return team.replace(/\s+/g, '_').replace(/[^\w-]/g, '');
}

// ----------------
// Save Functions
// ----------------

// Temporary save (frequent updates)
function saveTemporary() {
    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    const data = lists.map(listId => 
        Array.from(document.getElementById(listId)?.children || [])
            .map(item => item.id) // store string IDs
    );

    fetch(`/strategy/picklist/submit/?comp=${encodeURIComponent(comp_code)}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(response => {
        lastTimestamp = response.timestamp;
    })
    .catch(err => console.error("Error saving temporary:", err));
}

// Save to database (manual or auto-save)
function saveToDB() {
    const saveButton = document.querySelector('.save-button');
    const statusDiv = document.querySelector('.save-status');
    const statusMessage = document.querySelector('.status-message');
    saveButton.disabled = true;

    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    const data = lists.map(listId => 
        Array.from(document.getElementById(listId)?.children || [])
            .map(item => item.id)
    );

    fetch(`/strategy/picklist/submit/?comp=${encodeURIComponent(comp_code)}&save_to_db=true`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        triggerHapticFeedback();
        statusDiv.style.display = 'block';
        statusDiv.classList.add('success');
        statusDiv.classList.remove('error');
        statusMessage.textContent = 'Sent to database!';
        saveButton.classList.add('success');

        setTimeout(() => {
            statusDiv.style.display = 'none';
            saveButton.classList.remove('success');
            saveButton.disabled = false;
        }, 3000);
    })
    .catch(error => {
        console.error('Error saving to database:', error);
        statusDiv.style.display = 'block';
        statusDiv.classList.add('error');
        statusDiv.classList.remove('success');
        statusMessage.textContent = 'Error saving to database. Please try again.';
        saveButton.disabled = false;

        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    });
}

// Reset inactivity timer for auto-save
function resetInactivityTimer() {
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveToDB();
    }, INACTIVITY_TIMEOUT);
}

// ----------------
// Drag & Drop Functions
// ----------------

// Create team element for a list
function createTeamElement(team) {
    const safeId = sanitizeId(team);
    return `
        <li draggable="true"
            ondragstart="onDragStart(event)"
            class="picklist_teams"
            ondrop="onDrop(event)"
            ondragover="onDragOver(event)"
            id="${safeId}">
            <p>${team}</p>
            <input type="checkbox" onchange="chosen(event)">
        </li>
    `;
}

// Handle drag start
function onDragStart(ev) {
    draggedItem = ev.target;
    ev.dataTransfer.setData("team_number_id", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
    draggedItem.classList.add('being-dragged');
    resetInactivityTimer();
}

// Handle drag over
function onDragOver(ev) {
    ev.preventDefault();
    const list = getListElement(ev.target);
    if (!list || !draggedItem) return;

    const items = Array.from(list.children).filter(i => i !== draggedItem);
    if (items.length === 0) {
        list.appendChild(draggedItem);
        return;
    }

    const mouseY = ev.clientY;
    let closestItem = null;
    let closestDistance = Infinity;

    items.forEach(item => {
        const rect = item.getBoundingClientRect();
        const distance = Math.abs(mouseY - (rect.top + rect.height / 2));
        if (distance < closestDistance) {
            closestDistance = distance;
            closestItem = item;
        }
    });

    if (closestItem) {
        const rect = closestItem.getBoundingClientRect();
        const beforeOrAfter = mouseY < rect.top + rect.height / 2;
        list.insertBefore(draggedItem, beforeOrAfter ? closestItem : closestItem.nextSibling);
    }

    resetInactivityTimer();
}

// Handle drop
function onDrop(ev) {
    ev.preventDefault();
    const list = getListElement(ev.target);
    if (!list) return;

    const droppedItem = document.getElementById(ev.dataTransfer.getData("team_number_id"));
    if (droppedItem && draggedItem) {
        if (!list.contains(droppedItem)) list.appendChild(droppedItem);
        draggedItem.classList.remove('being-dragged');
        draggedItem = null;
        saveTemporary();
    }
    resetInactivityTimer();
}

// Get parent list element
function getListElement(element) {
    if (!element) return null;
    if (element.classList.contains('lists')) return element;
    if (element.parentNode?.classList.contains('lists')) return element.parentNode;
    if (element.parentNode?.parentNode?.classList.contains('lists')) return element.parentNode.parentNode;
    return null;
}

// ----------------
// Checkbox Function
// ----------------
function chosen(ev) {
    const listItem = ev.target.parentNode;
    const noPick = document.getElementById("no_pick");

    if (ev.target.checked) {
        noPick.appendChild(listItem);
        ev.target.checked = false;

        const strike = listItem.querySelector("s");
        if (strike) {
            const normal = document.createElement("p");
            normal.innerHTML = strike.innerHTML;
            strike.replaceWith(normal);
        }
    }
    saveTemporary();
    resetInactivityTimer();
}

// ----------------
// Fetch Updates with Throttling
// ----------------
function fetchUpdates() {
    if (isFetching) return;
    isFetching = true;

    fetch(`/strategy/picklist/submit/?comp=${encodeURIComponent(comp_code)}&timestamp=${lastTimestamp}&t=${Date.now()}`, {
        headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
    })
    .then(res => res.json())
    .then(response => {
        if (response.status === 'updated') {
            lastTimestamp = response.timestamp;
            updateLists(response.data);
        } else if (response.status === 'no_change') {
            lastTimestamp = response.timestamp;
        }
    })
    .catch(err => console.error('Error fetching updates:', err))
    .finally(() => isFetching = false);
}

// Update lists with new data
function updateLists(data) {
    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];

    lists.forEach((listId, index) => {
        const list = document.getElementById(listId);
        if (!list) return;

        const currentTeams = Array.from(list.children).map(item => item.id);
        const newTeams = data[index] || [];

        if (JSON.stringify(currentTeams) !== JSON.stringify(newTeams) && !draggedItem) {
            list.innerHTML = newTeams.map(team => createTeamElement(team)).join('');
        }
    });
}

// ----------------
// Initialize
// ----------------
document.addEventListener('DOMContentLoaded', function() {
    fetchUpdates();
    setInterval(fetchUpdates, FETCH_UPDATE_INTERVAL);
    resetInactivityTimer();
});
