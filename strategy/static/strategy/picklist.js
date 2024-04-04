
function onDragStart(ev) {
    ev.dataTransfer.setData("team_number_id", ev.target.id);
}

function onDragOver(ev) {
    ev.preventDefault();
}

function onDrop(ev) {
    ev.preventDefault();
    console.log(ev.target)
    if(ev.target.parentNode.className == "lists") {
        ev.target.after(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    } else if(ev.target.className == "lists") {
        ev.target.appendChild(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    } else {
        ev.target.parentNode.after(document.getElementById(ev.dataTransfer.getData("team_number_id")));
    }
    
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
}

function save() {
    var no_pick = document.getElementById("no_pick").getElementsByTagName("p");
    var first_pick = document.getElementById("1st_pick").getElementsByTagName("p");
    var second_pick = document.getElementById("2nd_pick").getElementsByTagName("p");
    var third_pick = document.getElementById("3rd_pick").getElementsByTagName("p");
    var dnp = document.getElementById("dnp").getElementsByTagName("p");
    for(i = 0; i < firstPick.length; i++) {
        console.log(first_pick[i]);
    }
}