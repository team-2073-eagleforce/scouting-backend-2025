import QrScanner from "/static/scanner/qr-scanner.min.js";

const video = document.getElementById('qr-video');
const camQrResult = document.getElementById('cam-qr-result');
let prevResult = "";


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

function post_data_to_server(data) {
    fetch("", {
        method: 'POST',
        credentials: 'include',
        mode: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: (data)
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            console.log(data)
        })
}

// ####### Web Cam Scanning #######
function setResult(label, result) {
    let data = result.data;
    if (data !== prevResult && !data.includes("error")) {
        prevResult = data;
        console.log(data);
        label.innerText = data;
        label.style.color = 'teal';
        clearTimeout(label.highlightTimeout);
        label.highlightTimeout = setTimeout(() => label.style.color = 'inherit', 100);
        post_data_to_server(data);
    }
}

const scanner = new QrScanner(video, result => setResult(camQrResult, result), {
    highlightScanRegion: true,
    highlightCodeOutline: true,
});

scanner.start().then(() => {
    // List cameras after the scanner started to avoid listCamera's stream and the scanner's stream being requested
    // at the same time which can result in listCamera's unconstrained stream also being offered to the scanner.
    // Note that we can also start the scanner after listCameras, we just have it this way around in the demo to
    // start the scanner earlier.
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