const scoringFields = ["auto", "teleop", "trap", "climb"];

document.getElementById("match_button").onclick = () => {
    let match = document.getElementById("match").value
    fetch("", {
        method: 'POST',
        credentials: 'include',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: (match)
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            let dashboardTable = document.getElementById("dashboardTable");
            for (let alliance_number = 0; alliance_number < data["red_teams"].length; alliance_number++) {
                let redTeam = data["red_teams"][alliance_number];
                let redTeamRow = dashboardTable.insertRow();

                let redTeamScoringField = redTeamRow.insertCell();
                redTeamScoringField.appendChild(document.createTextNode("Red ".concat((alliance_number + 1).toString())));

                let redTeamNumber = redTeamRow.insertCell();
                redTeamNumber.appendChild(document.createTextNode(redTeam));

                for (let scoringField of scoringFields) {
                    let redTeamScoringField = redTeamRow.insertCell();
                    redTeamScoringField.appendChild(document.createTextNode(data["red"][redTeam][scoringField]));
                }
            }

            for (let alliance_number = 0; alliance_number < data["blue_teams"].length; alliance_number++) {
                let blueTeam = data["blue_teams"][alliance_number];
                let blueTeamRow = dashboardTable.insertRow();

                let blueTeamScoringField = blueTeamRow.insertCell();
                blueTeamScoringField.appendChild(document.createTextNode("Blue ".concat((alliance_number + 1).toString())));

                let blueTeamNumber = blueTeamRow.insertCell();
                blueTeamNumber.appendChild(document.createTextNode(blueTeam));

                for (let scoringField of scoringFields) {
                    let blueTeamScoringField = blueTeamRow.insertCell();
                    blueTeamScoringField.appendChild(document.createTextNode(data["blue"][blueTeam][scoringField]));
                }
            }
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