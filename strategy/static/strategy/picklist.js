let lastSaveTime = 0;
const SAVE_DELAY = 100;

// Create WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/picklist/${localStorage.getItem("comp")}/`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'picklist_update') {
        updateLists(data.picklist);
    }
};

// ... (keep all the existing functions) ...

function save() {
    // If we've saved too recently, skip this save
    if (Date.now() - lastSaveTime < SAVE_DELAY) {
        return;
    }

    lastSaveTime = Date.now();

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
    });
}

// Remove the fetchUpdates function and interval since we're using WebSocket now

// Add WebSocket error handling and reconnection
ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function() {
        new WebSocket(`ws://${window.location.host}/ws/picklist/${localStorage.getItem("comp")}/`);
    }, 1000);
};

ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
};
