let draggedItem = null;
let saveTimeout = null;
let lastUpdateTime = 0;
let lastTimestamp = 0;
const INACTIVITY_TIMEOUT = 5000; // 5 seconds of inactivity before auto-save
const FETCH_UPDATE_INTERVAL = 10000; // Fetch updates every 10 seconds
let isFetching = false; // To prevent overlapping fetch requests

// Function to save to JSON file (frequent updates)
function saveTemporary() {
    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    const data = lists.map(listId => 
        Array.from(document.getElementById(listId)?.children || [])
            .map(item => parseInt(item.id))
            .filter(id => !isNaN(id))
    );

    fetch(`/strategy/picklist/submit/?comp=${comp_code}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(response => {
        lastTimestamp = response.timestamp;
    });
}

// Function to save to database (infrequent updates)
function saveToDB() {
    const saveButton = document.querySelector('.save-button');
    const statusDiv = document.querySelector('.save-status');
    const statusMessage = document.querySelector('.status-message');
    
    saveButton.disabled = true;

    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    const data = lists.map(listId => 
        Array.from(document.getElementById(listId)?.children || [])
            .map(item => parseInt(item.id))
            .filter(id => !isNaN(id))
    );

    fetch(`/strategy/picklist/submit/?comp=${comp_code}&save_to_db=true`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token if needed
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
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
        console.error('Error:', error);
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

// Function to reset the inactivity timer
function resetInactivityTimer() {
    if (saveTimeout) {
        clearTimeout(saveTimeout);
    }
    saveTimeout = setTimeout(() => {
        saveToDB(); // Auto-save to the database after inactivity
    }, INACTIVITY_TIMEOUT);
}

// Function to create team element
function createTeamElement(team) {
    return `
        <li draggable="true" 
            ondragstart="onDragStart(event)" 
            class="picklist_teams" 
            ondrop="onDrop(event)" 
            ondragover="onDragOver(event)" 
            id="${team}">
            <p>${team}</p>
            <input type="checkbox" onchange="chosen(event)">
        </li>
    `;
}

// Function to fetch updates with throttling
function fetchUpdates() {
    if (isFetching) return; // Prevent overlapping requests
    isFetching = true;

    fetch(`/strategy/picklist/submit/?comp=${comp_code}&timestamp=${lastTimestamp}&t=${Date.now()}`, {
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => response.json())
    .then(response => {
        if (response.status === 'updated') {
            lastTimestamp = response.timestamp;
            updateLists(response.data);
        } else if (response.status === 'no_change') {
            lastTimestamp = response.timestamp;
        }
        isFetching = false;
    })
    .catch(error => {
        console.error('Error fetching updates:', error);
        isFetching = false;
    });
}

// Function to update the lists with new data
function updateLists(data) {
    const lists = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    
    lists.forEach((listId, index) => {
        const list = document.getElementById(listId);
        if (!list) return;

        const currentTeams = Array.from(list.children).map(item => parseInt(item.id));
        const newTeams = data[index] || [];

        // Only update if there are actual changes and we're not currently dragging
        if (JSON.stringify(currentTeams) !== JSON.stringify(newTeams) && !draggedItem) {
            list.innerHTML = newTeams.map(team => createTeamElement(team)).join('');
        }
    });
}

// Modified save function
function save() {
    if (saveTimeout) {
        clearTimeout(saveTimeout);
    }
    saveTemporary();
    resetInactivityTimer(); // Reset the inactivity timer
}

function onDragStart(ev) {
    draggedItem = ev.target;
    ev.dataTransfer.setData("team_number_id", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
    draggedItem.classList.add('being-dragged');
    resetInactivityTimer(); // Reset the inactivity timer
}

function onDragOver(ev) {
    ev.preventDefault();
    const list = getListElement(ev.target);
    if (!list || !draggedItem) return;

    const items = Array.from(list.children);
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
        
        if (beforeOrAfter) {
            list.insertBefore(draggedItem, closestItem);
        } else {
            list.insertBefore(draggedItem, closestItem.nextSibling);
        }
    }
    resetInactivityTimer(); // Reset the inactivity timer
}

function onDrop(ev) {
    ev.preventDefault();
    const list = getListElement(ev.target);
    if (!list || !draggedItem) return;

    const droppedItem = document.getElementById(ev.dataTransfer.getData("team_number_id"));
    if (droppedItem) {
        const mouseY = ev.clientY;
        const items = Array.from(list.children);
        let insertPosition = null;

        for (let i = 0; i < items.length; i++) {
            const rect = items[i].getBoundingClientRect();
            if (mouseY < rect.bottom) {
                insertPosition = items[i];
                break;
            }
        }

        if (insertPosition) {
            list.insertBefore(droppedItem, insertPosition);
        } else {
            list.appendChild(droppedItem);
        }
        
        save();
    }

    if (draggedItem) {
        draggedItem.classList.remove('being-dragged');
    }
    draggedItem = null;
    resetInactivityTimer(); // Reset the inactivity timer
}

function getListElement(element) {
    if (element.classList.contains('lists')) {
        return element;
    } else if (element.parentNode && element.parentNode.classList.contains('lists')) {
        return element.parentNode;
    } else if (element.parentNode && element.parentNode.parentNode && element.parentNode.parentNode.classList.contains('lists')) {
        return element.parentNode.parentNode;
    }
    return null;
}

function chosen(ev) {
    const listItem = ev.target.parentNode;
    const noPick = document.getElementById("no_pick");
    
    if(ev.target.checked) {
        noPick.appendChild(listItem);
        ev.target.checked = false;
        
        if (listItem.querySelector("s")) {
            var normal = document.createElement("p");
            normal.innerHTML = listItem.querySelector("s").innerHTML;
            listItem.querySelector("s").replaceWith(normal);
        }
    }
    save();
    resetInactivityTimer(); // Reset the inactivity timer
}

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

function triggerHapticFeedback() {
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

// Start the periodic updates when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch
    fetchUpdates();
    
    // Set up periodic updates with throttling
    setInterval(fetchUpdates, FETCH_UPDATE_INTERVAL);

    // Start the inactivity timer
    resetInactivityTimer();
});