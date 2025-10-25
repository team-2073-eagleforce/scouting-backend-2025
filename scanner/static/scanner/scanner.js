import QrScanner from "/static/scanner/qr-scanner.min.js";

const video = document.getElementById('qr-video');
const camQrResult = document.getElementById('cam-qr-result');
let prevResult = "";

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to send QR data to Django backend
function post_data_to_server(data) {
    const feedbackElement = document.getElementById('scan-feedback');
    feedbackElement.textContent = 'Uploading...';
    feedbackElement.style.color = 'orange';
    
    // Parse the QR data to show team/match info
    let qrData;
    try {
        qrData = JSON.parse(data);
    } catch (e) {
        feedbackElement.textContent = 'Invalid QR code format';
        feedbackElement.style.color = 'red';
        return;
    }
    
    fetch("/scanner/", {
        method: 'POST',
        credentials: 'include',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: data  // Send raw QR data
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || "Unknown error") });
        }
        return response.json();
    })
    .then(response => {
        console.log("Server Response:", response);
        
        // Show success with specific details
        const teamNum = qrData.teamNumber || 'Unknown';
        const matchNum = qrData.matchNumber || 'Unknown';
        
        feedbackElement.textContent = `✓ ${response.confirmation} - Team ${teamNum}, Match ${matchNum}`;
        feedbackElement.style.color = 'green';
        
        // Clear feedback after 3 seconds
        setTimeout(() => {
            feedbackElement.textContent = '';
        }, 3000);
    })
    .catch(error => {
        console.error("Error:", error.message);
        feedbackElement.textContent = `✗ Upload failed: ${error.message}`;
        feedbackElement.style.color = 'red';
        
        // Clear error after 5 seconds
        setTimeout(() => {
            feedbackElement.textContent = '';
        }, 5000);
    });
}

// ####### Web Cam Scanning #######
function setResult(label, result) {
    let data = result.data;
    if (data !== prevResult && !data.includes("error")) {
        prevResult = data;
        console.log("Scanned Data:", data);
        
        // Show truncated QR data for confirmation
        const truncated = data.length > 50 ? data.substring(0, 50) + '...' : data;
        label.innerText = truncated;
        label.style.color = 'teal';
        clearTimeout(label.highlightTimeout);
        label.highlightTimeout = setTimeout(() => label.style.color = 'inherit', 2000);
        
        post_data_to_server(data);
    }
}

const scanner = new QrScanner(video, result => setResult(camQrResult, result), {
    highlightScanRegion: true,
    highlightCodeOutline: true,
});

scanner.start().then(() => {
    QrScanner.listCameras(true).then(cameras => cameras.forEach(camera => {
        const option = document.createElement('option');
        option.value = camera.id;
        option.text = camera.label;
    }));
});

document.getElementById('start-button').addEventListener('click', () => {
    scanner.start();
});

document.getElementById('stop-button').addEventListener('click', () => {
    scanner.stop();
});
