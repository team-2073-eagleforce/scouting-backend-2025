let prevClassName;

function sortTable(n, className) {
    let tags = document.getElementsByClassName(className);
    for (let i = 0; i < tags.length; i++) {
        tags[i].setAttribute("style", "color: LightGreen;")
    }

    if (prevClassName !== undefined && prevClassName !== className) {
        tags = document.getElementsByClassName(prevClassName);
        for (let i = 0; i < tags.length; i++) {
            tags[i].setAttribute("style", "color: black;")
        }
    }
    prevClassName = className

    let table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("rankings_table");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "desc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir === "asc" || className === "team_number") {
                console.log(parseFloat(x.innerHTML))
                console.log(parseFloat(y.innerHTML))
                if (parseFloat(x.innerHTML) > parseFloat(y.innerHTML)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir === "desc") {
                if (parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount === 0 && dir === "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }

    let elements = document.getElementsByClassName("rank")
    for (let index = 0; index < elements.length; index++) {
        elements[index].innerHTML = index + 1;
    }
}

