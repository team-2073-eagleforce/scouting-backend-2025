import QrScanner from "/static/scanner/qr-scanner.min.js";

const video = document.getElementById('qr-video');
const camQrResult = document.getElementById('cam-qr-result');
let prevResult = "";
const pendingScans = new Set();

// Validation functions
function validateScanData(scanData) {
    const errors = [];
    
    const required = ['teamNumber', 'matchNumber', 'name', 'comp_code'];
    for (const field of required) {
        if (!scanData[field] || String(scanData[field]).trim() === '') {
            errors.push(`Missing ${field}`);
        }
    }
    
    const teamNum = parseInt(scanData.teamNumber);
    if (isNaN(teamNum) || teamNum <= 0 || teamNum > 99999) {
        errors.push('Invalid team number');
    }
    
    const matchNum = parseInt(scanData.matchNumber);
    if (isNaN(matchNum) || matchNum <= 0 || matchNum > 999) {
        errors.push('Invalid match number');
    }
    
    const name = String(scanData.name).trim();
    if (name.length < 2 || name.length > 32) {
        errors.push('Scout name must be 2-32 characters');
    }
    
    return errors;
}

function showValidationDialog(errors, scanData) {
    const message = `Scan validation failed:\n${errors.join('\n')}\n\nOptions:\n1. Skip this scan\n2. Edit data manually`;
    
    if (confirm(message + '\n\nClick OK to edit manually, Cancel to skip')) {
        return showEditDialog(scanData);
    }
    return null;
}

function showEditDialog(scanData) {
    const teamNumber = prompt('Team Number:', scanData.teamNumber || '');
    if (teamNumber === null) return null;
    
    const matchNumber = prompt('Match Number:', scanData.matchNumber || '');
    if (matchNumber === null) return null;
    
    const name = prompt('Scout Name:', scanData.name || '');
    if (name === null) return null;
    
    const comp_code = prompt('Competition Code:', scanData.comp_code || '');
    if (comp_code === null) return null;
    
    return {
        ...scanData,
        teamNumber: teamNumber.trim(),
        matchNumber: matchNumber.trim(),
        name: name.trim(),
        comp_code: comp_code.trim()
    };
}

function showMessage(message, color = 'inherit') {
    if (camQrResult) {
        camQrResult.textContent = message;
        camQrResult.style.color = color;
        
        setTimeout(() => {
            camQrResult.style.color = 'inherit';
        }, 3000);
    }
    
    const feedbackEl = document.getElementById('scan-feedback');
    if (feedbackEl) {
        feedbackEl.textContent = message;
        feedbackEl.style.color = color;
    }
}

async function handleSuccessfulScan(decodedText) {
    if (decodedText === prevResult || pendingScans.has(decodedText)) {
        return;
    }

    prevResult = decodedText;
    pendingScans.add(decodedText);
    
    try {
        const scanData = JSON.parse(decodedText);
        const errors = validateScanData(scanData);
        
        let finalData = scanData;
        if (errors.length > 0) {
            showMessage(`Validation errors: ${errors.join(', ')}`, 'red');
            finalData = showValidationDialog(errors, scanData);
            
            if (!finalData) {
                showMessage('Scan skipped', 'orange');
                return;
            }
            
            const newErrors = validateScanData(finalData);
            if (newErrors.length > 0) {
                showMessage(`Still invalid: ${newErrors.join(', ')}`, 'red');
                return;
            }
        }
        
        await sendToServer(finalData);
        showMessage('Scan successful!', 'green');
        
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
        
    } catch (error) {
        console.error('Failed to process scan:', error);
        showMessage('Invalid QR code format', 'red');
    } finally {
        pendingScans.delete(decodedText);
    }
}

async function sendToServer(data) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        throw new Error('CSRF token not found');
    }

    const response = await fetch('/scanner/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        if (response.status === 400 && errorData.error === 'Validation failed') {
            showMessage('Server rejected data - validation failed', 'red');
        } else {
            showMessage('Server error - please try again', 'red');
        }
        throw new Error(errorData.error || `HTTP ${response.status}`);
    }

    return response.json();
}

const qrScanner = new QrScanner(video, result => handleSuccessfulScan(result.data), {
    highlightScanRegion: true,
    highlightCodeOutline: true,
});

qrScanner.start().then(() => {
    QrScanner.listCameras(true).then(cameras => cameras.forEach(camera => {
        const option = document.createElement('option');
        option.value = camera.id;
        option.text = camera.label;
        document.getElementById('camera-select')?.appendChild(option);
    }));
});

document.getElementById('start-button')?.addEventListener('click', () => {
    qrScanner.start();
});

document.getElementById('stop-button')?.addEventListener('click', () => {
    qrScanner.stop();
});

document.getElementById('camera-select')?.addEventListener('change', (event) => {
    qrScanner.setCamera(event.target.value);
});
