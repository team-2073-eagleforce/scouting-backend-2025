console.log("Script loaded");
        
const scoringFields = ["auto", "autoleave", "L1", "L2", "L3", "L4", "net", "processor", "removed", "climb", "defense"];

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded");
    
    document.getElementById("match_button").onclick = function() {
        console.log("Button clicked");
        let match = document.getElementById("match").value;
        console.log("Match value:", match);

        fetch("", {
            method: 'POST',
            credentials: 'include',
            mode: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(match)
        })
        .then(response => {
            console.log("Response received:", response);
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            let dashboardTable = document.getElementById("dashboardTable");
            
            // Clear existing rows
            dashboardTable.innerHTML = '';

            // Red alliance
            for (let alliance_number = 0; alliance_number < data["red_teams"].length; alliance_number++) {
                let redTeam = data["red_teams"][alliance_number];
                let redTeamRow = dashboardTable.insertRow();

                let redTeamScoringField = redTeamRow.insertCell();
                redTeamScoringField.appendChild(document.createTextNode("Red " + (alliance_number + 1)));

                let redTeamNumber = redTeamRow.insertCell();
                redTeamNumber.appendChild(document.createTextNode(redTeam));

                for (let scoringField of scoringFields) {
                    let redTeamScoringField = redTeamRow.insertCell();
                    let value = data["red"][redTeam] && data["red"][redTeam][scoringField] !== undefined 
                        ? data["red"][redTeam][scoringField] 
                        : '0';
                    redTeamScoringField.appendChild(document.createTextNode(value));
                }
            }

            // Blue alliance
            for (let alliance_number = 0; alliance_number < data["blue_teams"].length; alliance_number++) {
                let blueTeam = data["blue_teams"][alliance_number];
                let blueTeamRow = dashboardTable.insertRow();

                let blueTeamScoringField = blueTeamRow.insertCell();
                blueTeamScoringField.appendChild(document.createTextNode("Blue " + (alliance_number + 1)));

                let blueTeamNumber = blueTeamRow.insertCell();
                blueTeamNumber.appendChild(document.createTextNode(blueTeam));

                for (let scoringField of scoringFields) {
                    let blueTeamScoringField = blueTeamRow.insertCell();
                    let value = data["blue"][blueTeam] && data["blue"][blueTeam][scoringField] !== undefined 
                        ? data["blue"][blueTeam][scoringField] 
                        : '0';
                    blueTeamScoringField.appendChild(document.createTextNode(value));
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
});

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