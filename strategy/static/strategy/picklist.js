
function onDragStart(ev) {
    ev.dataTransfer.setData("team_number_id", ev.target.id);
}

function onDragOver(ev) {
    ev.preventDefault();
}

function onDrop(ev) {
    ev.preventDefault();
    if(ev.target.parentNode.className == "lists") {
        ev.target.after(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    } else if(ev.target.className == "lists") {
        ev.target.appendChild(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    } else {
        ev.target.parentNode.after(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    }
    save(); // Auto-save when item is dropped
}

function chosen(ev) {
    if(ev.target.checked == true) {
        var strike = document.createElement("s");
        strike.innerHTML = ev.target.parentNode.querySelector("p").innerHTML;
        ev.target.parentNode.querySelector("p").replaceWith(strike);
    } else {
        var normal = document.createElement("p");
        normal.innerHTML = ev.target.parentNode.querySelector("s").innerHTML;
        ev.target.parentNode.querySelector("s").replaceWith(normal);
    }
    save(); // Auto-save when item is checked/unchecked
}

function save() {
    var no_pick = document.getElementById("no_pick").getElementsByTagName("p");
    var first_pick = document.getElementById("1st_pick").getElementsByTagName("p");
    var second_pick = document.getElementById("2nd_pick").getElementsByTagName("p");
    if(document.getElementById("3rd_pick") != null) {
        var third_pick = document.getElementById("3rd_pick").getElementsByTagName("p");
    }
    var dn_pick = document.getElementById("dnp").getElementsByTagName("p");

    var no_pick_list = []
    var first_pick_list = []
    var second_pick_list = []
    var third_pick_list = []
    var dn_pick_list = []
    for(i = 0; i < no_pick.length; i++) {
        no_pick_list.push(no_pick[i].innerHTML);
    }
    for(i = 0; i < first_pick.length; i++) {
        first_pick_list.push(first_pick[i].innerHTML);
    }
    for(i = 0; i < second_pick.length; i++) {
        second_pick_list.push(second_pick[i].innerHTML);
    }
    if(document.getElementById("3rd_pick") != null) {
        for(i = 0; i < third_pick.length; i++) {
            third_pick_list.push(third_pick[i].innerHTML);
        }
    }
    for(i = 0; i < dn_pick.length; i++) {
        dn_pick_list.push(dn_pick[i].innerHTML);
    }
    var picklist_save_data = [no_pick_list, first_pick_list, second_pick_list, third_pick_list, dn_pick_list]
    fetch(`/strategy/picklist/submit/?comp=${localStorage.getItem("comp")}`, {
        method: 'POST',
        credentials: 'include',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(picklist_save_data)
    })     
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function fetchUpdates() {
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
        updateLists(data);
    });
}

function updateLists(data) {
    // Update each list with the new data
    updateList("no_pick", data[0]);
    updateList("1st_pick", data[1]);
    updateList("2nd_pick", data[2]);
    if(document.getElementById("3rd_pick") != null) {
        updateList("3rd_pick", data[3]);
    }
    updateList("dnp", data[4]);
}

function updateList(listId, teams) {
    const list = document.getElementById(listId);
    // Only update if the content is different
    const currentTeams = Array.from(list.getElementsByTagName("p")).map(p => p.innerHTML);
    if (JSON.stringify(currentTeams) !== JSON.stringify(teams)) {
        // Clear existing items
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
        // Add new items
        teams.forEach(team => {
            const div = document.createElement("div");
            div.id = team;
            div.draggable = true;
            div.setAttribute("ondragstart", "onDragStart(event)");
            const p = document.createElement("p");
            p.innerHTML = team;
            div.appendChild(p);
            list.appendChild(div);
        });
    }
}

// Start periodic updates when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Update every 2 seconds
    setInterval(fetchUpdates, 1000);
});
