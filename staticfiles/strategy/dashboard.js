console.log("Script loaded");

const metricKeys = window.configMetrics ? window.configMetrics.map(m => m.key) : [];

if (window.dashboardInitialized) {
    console.warn('Dashboard already initialized');
} else {
    window.dashboardInitialized = true;

    document.addEventListener('DOMContentLoaded', function() {
        console.log("DOM loaded");
        
        const button = document.getElementById("match_button");
        if (!button) {
            console.error("Match button not found");
            return;
        }

        button.onclick = function(e) {
            e.preventDefault();
            console.log("Button clicked");
            
            const dashboardTable = document.getElementById("dashboardTable");
            if (!dashboardTable) {
                console.error("Table not found");
                return;
            }

            let match = document.getElementById("match").value;
            if (!match) {
                console.warn("No match value entered");
                return;
            }

            dashboardTable.innerHTML = '';
            console.log("Table cleared, starting fetch");

            fetch("", {
                method: 'POST',
                credentials: 'include',
                mode: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    match_number: parseInt(match) || 0,
                    quantifier: document.getElementById('quantifier').value
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Server error');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (!data.red || !data.blue) {
                    throw new Error('Invalid data format received from server');
                }
                console.log("Processing data for match:", match);

                // Process red alliance
                (data.red_teams || []).forEach((redTeam, index) => {
                    const row = dashboardTable.insertRow();
                    row.insertCell().textContent = `Red ${index + 1}`;
                    row.insertCell().textContent = redTeam;
                    row.insertCell().textContent = data.red[redTeam]?.autoLeave || '0';
                    
                    metricKeys.forEach(key => {
                        row.insertCell().textContent = data.red[redTeam]?.[key] || '0';
                    });
                    
                    row.insertCell().textContent = data.red[redTeam]?.driverRanking || '0';
                    row.insertCell().textContent = data.red[redTeam]?.defenseRanking || '0';
                    row.insertCell().textContent = data.red[redTeam]?.start_pos || '0';
                });

                // Process blue alliance
                (data.blue_teams || []).forEach((blueTeam, index) => {
                    const row = dashboardTable.insertRow();
                    row.insertCell().textContent = `Blue ${index + 1}`;
                    row.insertCell().textContent = blueTeam;
                    row.insertCell().textContent = data.blue[blueTeam]?.autoLeave || '0';
                    
                    metricKeys.forEach(key => {
                        row.insertCell().textContent = data.blue[blueTeam]?.[key] || '0';
                    });
                    
                    row.insertCell().textContent = data.blue[blueTeam]?.driverRanking || '0';
                    row.insertCell().textContent = data.blue[blueTeam]?.defenseRanking || '0';
                    row.insertCell().textContent = data.blue[blueTeam]?.start_pos || '0';
                });

                console.log("Table population complete");
            })
            .catch(error => {
                console.error('Error:', error);
                const dashboardTable = document.getElementById("dashboardTable");
                if (dashboardTable) {
                    dashboardTable.innerHTML = `<tr><td colspan="100">Error: ${error.message}</td></tr>`;
                }
            });
        };
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