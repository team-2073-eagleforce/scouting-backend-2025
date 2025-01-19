let draggedItem = null;
let saveTimeout = null;
let lastUpdateTime = 0;

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
    });
}

// Function to save to database (infrequent updates)
function saveToDB() {
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
        },
        body: JSON.stringify(data)
    }).then(() => {
        console.log('Saved to database successfully');
    }).catch(error => {
        console.error('Error saving to database:', error);
    });
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

// Function to fetch updates
function fetchUpdates() {
    fetch(`/strategy/picklist/submit/?comp=${comp_code}&t=${Date.now()}`, {
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data && Array.isArray(data)) {
            updateLists(data);
        }
    })
    .catch(error => console.error('Error fetching updates:', error));
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
}

function onDragStart(ev) {
    draggedItem = ev.target;
    ev.dataTransfer.setData("team_number_id", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
    draggedItem.classList.add('being-dragged');
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
}

// Start the periodic updates when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch
    fetchUpdates();
    
    // Set up periodic updates
    setInterval(fetchUpdates, 1000);
});
