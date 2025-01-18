let draggedItem = null;

function onDragStart(ev) {
    draggedItem = ev.target;
    ev.dataTransfer.setData("team_number_id", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
    // Add a class to indicate dragging state
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
    }

    // Remove the dragging class
    if (draggedItem) {
        draggedItem.classList.remove('being-dragged');
    }
    draggedItem = null;
    save();
}

// Helper function to get the list element
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

function save() {
    var no_pick = Array.from(document.getElementById("no_pick").getElementsByTagName("li")).map(li => li.id);
    var first_pick = Array.from(document.getElementById("1st_pick").getElementsByTagName("li")).map(li => li.id);
    var second_pick = Array.from(document.getElementById("2nd_pick").getElementsByTagName("li")).map(li => li.id);
    var third_pick = [];
    if (document.getElementById("3rd_pick")) {
        third_pick = Array.from(document.getElementById("3rd_pick").getElementsByTagName("li")).map(li => li.id);
    }
    var dn_pick = Array.from(document.getElementById("dnp").getElementsByTagName("li")).map(li => li.id);

    var picklist_save_data = [no_pick, first_pick, second_pick, third_pick, dn_pick];

    fetch(`/strategy/picklist/submit/?comp=${localStorage.getItem("comp")}`, {
        method: 'POST',
        credentials: 'include',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(picklist_save_data)
    });
}

function fetchUpdates() {
    if (draggedItem) return; // Don't update while dragging

    fetch(`/strategy/picklist/submit/?comp=${localStorage.getItem("comp")}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            updateLists(data);
        }
    })
    .catch(error => {
        console.error('Error fetching updates:', error);
    });
}

function updateLists(data) {
    if (!data || !Array.isArray(data)) return;
    
    const listIds = ['no_pick', '1st_pick', '2nd_pick', '3rd_pick', 'dnp'];
    
    // Store current checkbox states
    const checkboxStates = new Map();
    document.querySelectorAll('.picklist_teams').forEach(li => {
        const checkbox = li.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkboxStates.set(li.id, checkbox.checked);
        }
    });

    data.forEach((teams, index) => {
        const listElement = document.getElementById(listIds[index]);
        if (!listElement) return;
        
        // Only update if this list doesn't contain the dragged item
        if (draggedItem && listElement.contains(draggedItem)) return;

        // Update list content
        listElement.innerHTML = teams.map(team => `
            <li draggable="true" 
                ondragstart="onDragStart(event)" 
                class="picklist_teams" 
                ondrop="onDrop(event)" 
                ondragover="onDragOver(event)" 
                id="${team}">
                ${checkboxStates.get(team) ? 
                    `<s>${team}</s>` : 
                    `<p>${team}</p>`}
                <input type="checkbox" 
                       onchange="chosen(event)" 
                       ${checkboxStates.get(team) ? 'checked' : ''}>
            </li>
        `).join('');
    });
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

// Start the periodic updates when the page loads
document.addEventListener('DOMContentLoaded', function() {
    setInterval(fetchUpdates, 2000);
});
