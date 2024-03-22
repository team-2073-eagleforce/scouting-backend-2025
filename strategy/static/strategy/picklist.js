function onDragStart(ev) {
    ev.dataTransfer.setData("text", ev.target.firstChild.innerHTML);
}

function onDragOver(ev) {
    ev.preventDefault();
}

function onDrop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    ev.target.appendChild(document.getElementById(data));
}