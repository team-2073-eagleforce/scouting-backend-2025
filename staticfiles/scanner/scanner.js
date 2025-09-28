import QrScanner from "/static/scanner/qr-scanner.min.js";

// --- Global Variables ---
const video = document.getElementById('qr-video');
const camQrResult = document.getElementById('cam-qr-result');
let prevResult = ""; // Used to prevent duplicate processing of the same QR code

let scanCache = [];
const CACHE_LIMIT = 10; // How many scans to hold before sending automatically

// --- Caching Logic ---

/**
 * Saves the current scan cache to the browser's localStorage.
 */
function saveCache() {
    localStorage.setItem('scanCache', JSON.stringify(scanCache));
    updateCacheIndicator();
}

/**
 * Loads any existing cache from localStorage when the page loads.
 */
function loadCache() {
    const cachedData = localStorage.getItem('scanCache');
    if (cachedData) {
        scanCache = JSON.parse(cachedData);
        console.log(`Loaded ${scanCache.length} scans from a previous session.`);
        // If there's old data, try to send it immediately
        if (scanCache.length > 0) {
            sendCachedScans();
        }
    }
    updateCacheIndicator();
}

/**
 * Updates the UI element showing the number of cached scans.
 * Make sure you have an element with id="cache-indicator" in your HTML.
 */
function updateCacheIndicator() {
    const indicator = document.getElementById('cache-indicator');
    if (indicator) {
        indicator.textContent = `Cached Scans: ${scanCache.length}`;
    }
}

/**
 * Handles the result of a successful QR code scan.
 * @param {string} decodedText - The JSON string data from the QR code.
 */
function handleSuccessfulScan(decodedText) {
    try {
        // Prevent processing the same scan multiple times in a row
        if (decodedText === prevResult) {
            return;
        }
        prevResult = decodedText;
        camQrResult.textContent = 'Successful Scan!';


        const scanData = JSON.parse(decodedText);
        scanCache.push(scanData);
        saveCache(); // Save to localStorage after every successful scan

        console.log(`Scan cached. Total cached: ${scanCache.length}`);

        // Provide user feedback
        const feedbackEl = document.getElementById('scan-feedback');
        if (feedbackEl) {
            feedbackEl.textContent = `Scan successful! Cached: ${scanCache.length}`;
            feedbackEl.style.color = 'green';
        }

        // If the cache has reached its limit, send the data
        if (scanCache.length >= CACHE_LIMIT) {
            sendCachedScans();
        }
    } catch (error) {
        console.error("Failed to parse QR code JSON:", error);
        const feedbackEl = document.getElementById('scan-feedback');
        if (feedbackEl) {
            feedbackEl.textContent = "Error: Invalid QR Code Data.";
            feedbackEl.style.color = 'red';
        }
    }
}

/**
 * Sends the entire batch of cached scans to the server.
 */
function sendCachedScans() {
    if (scanCache.length === 0) {
        return; // Don't send if there's nothing to send
    }

    // Get the CSRF token from the Django template
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (!csrfToken) {
        console.error("CSRF token not found!");
        return;
    }

    const feedbackEl = document.getElementById('scan-feedback');
    if (feedbackEl) {
        feedbackEl.textContent = `Syncing ${scanCache.length} scans...`;
        feedbackEl.style.color = 'blue';
    }


    fetch('/scanner/', { // The URL to your Django view
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken // Crucial for Django POST requests
        },
        body: JSON.stringify(scanCache) // Send the entire cache array
    })
    .then(response => {
        if (!response.ok) {
            // If the server returns an error, we throw an error to keep the data cached
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Successfully sent cached scans:', data);
        if (feedbackEl) {
            feedbackEl.textContent = data.confirmation;
            feedbackEl.style.color = 'green';
        }

        // If the send was successful, clear the cache
        scanCache = [];
        localStorage.removeItem('scanCache');
        updateCacheIndicator();
    })
    .catch((error) => {
        console.error('Error sending cached scans:', error);
        if (feedbackEl) {
            feedbackEl.textContent = "Error sending data. Scans are saved and will be sent later.";
            feedbackEl.style.color = 'red';
        }
        // If there's an error (e.g., no network), the data remains safely in the cache to be sent later
    });
}

// --- QR Scanner Initialization ---

const qrScanner = new QrScanner(video, result => handleSuccessfulScan(result.data), {
    highlightScanRegion: true,
    highlightCodeOutline: true,
});

qrScanner.start().then(() => {
    // Optional: Populate a camera dropdown list
    QrScanner.listCameras(true).then(cameras => cameras.forEach(camera => {
        const option = document.createElement('option');
        option.value = camera.id;
        option.text = camera.label;
        document.getElementById('camera-select')?.appendChild(option); // Add a <select id="camera-select"></select> to your HTML
    }));
});


// --- Event Listeners ---

// When the page first loads, load any data from previous sessions
window.addEventListener('load', loadCache);

// Also try to send any remaining data when the user closes or navigates away from the page
// This is a failsafe; the load event is the primary mechanism for data recovery.
window.addEventListener('beforeunload', sendCachedScans);

// Button listeners
document.getElementById('start-button').addEventListener('click', () => {
    qrScanner.start();
});

document.getElementById('stop-button').addEventListener('click', () => {
    qrScanner.stop();
});

// Add a manual sync button in case the user wants to force an upload
// Make sure you have a <button id="manual-sync-button">Sync Data</button> in your HTML
document.getElementById('manual-sync-button')?.addEventListener('click', sendCachedScans);
