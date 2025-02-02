console.log("Replay System Loading...");

// Field position configurations
const fieldPositions = {
    "A": { x: 278 * (512/800), y: 115 * (288/400) },
    "B": { x: 278 * (512/800), y: 160 * (288/400) },
    "C": { x: 285 * (512/800), y: 200 * (288/400) },
    "D": { x: 330 * (512/800), y: 220 * (288/400) },
    "E": { x: 375 * (512/800), y: 220 * (288/400) },
    "F": { x: 420 * (512/800), y: 200 * (288/400) },
    "G": { x: 430 * (512/800), y: 160 * (288/400) },
    "H": { x: 430 * (512/800), y: 115 * (288/400) },
    "I": { x: 420 * (512/800), y: 70 * (288/400) },
    "J": { x: 375 * (512/800), y: 50 * (288/400) },
    "K": { x: 330 * (512/800), y: 50 * (288/400) },
    "L": { x: 285 * (512/800), y: 70 * (288/400) },
    "processor": { x: 390 * (512/800), y: 265 * (288/400) },
    "groundA": { x: 175 * (512/800), y: 85 * (288/400) },
    "groundB": { x: 175 * (512/800), y: 150 * (288/400) },
    "groundC": { x: 175 * (512/800), y: 220 * (288/400) },
    "sourceA": { x: 88 * (512/800), y: 90 * (288/400) },
    "sourceB": { x: 88 * (512/800), y: 232 * (288/400) }
};

class ReplaySystem {
    constructor() {
        console.log("Initializing Replay System");
        this.canvas = document.getElementById('replayCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentPath = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.animationFrame = null;
        
        this.initializeCanvas();
        this.setupEventListeners();
        this.selectedPoint = null;
        this.isDragging = false;
        this.positions = JSON.parse(JSON.stringify(fieldPositions)); // Clone positions
        this.enableDragMode();
    }

    enableDragMode() {
        // Add print button
        const printButton = document.createElement('button');
        printButton.textContent = 'Print Positions';
        printButton.style.position = 'absolute';
        printButton.style.top = '10px';
        printButton.style.left = '10px';
        printButton.style.padding = '10px';
        printButton.style.backgroundColor = '#007bff';
        printButton.style.color = '#fff';
        printButton.style.border = 'none';
        printButton.style.borderRadius = '5px';
        printButton.style.cursor = 'pointer';
        printButton.onclick = () => this.printPositions();
        document.body.appendChild(printButton);
    
        // Mouse event listeners
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
    
        // Start rendering loop
        this.renderCalibrationView();
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: (e.clientX - rect.left) * (this.canvas.width / rect.width),
            y: (e.clientY - rect.top) * (this.canvas.height / rect.height)
        };
    }

    handleMouseDown(e) {
        const mousePos = this.getMousePos(e);
        const hitRadius = 10;

        // Check if we clicked on a point
        for (const [key, pos] of Object.entries(this.positions)) {
            const dx = mousePos.x - pos.x;
            const dy = mousePos.y - pos.y;
            if (dx * dx + dy * dy < hitRadius * hitRadius) {
                this.selectedPoint = key;
                this.isDragging = true;
                break;
            }
        }
    }

    handleMouseMove(e) {
        if (this.isDragging && this.selectedPoint) {
            const mousePos = this.getMousePos(e);
            this.positions[this.selectedPoint] = {
                x: Math.round(mousePos.x),
                y: Math.round(mousePos.y)
            };
        }
    }

    handleMouseUp() {
        this.isDragging = false;
        this.selectedPoint = null;
    }

    renderCalibrationView() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw all points
        for (const [key, pos] of Object.entries(this.positions)) {
            // Draw point
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = this.selectedPoint === key ? 'red' : 'blue';
            this.ctx.fill();

            // Draw label
            this.ctx.fillStyle = 'black';
            this.ctx.font = '12px Arial';
            this.ctx.fillText(key, pos.x + 10, pos.y + 10);
        }

        requestAnimationFrame(() => this.renderCalibrationView());
    }

    printPositions() {
        const formattedPositions = {};
        for (const [key, pos] of Object.entries(this.positions)) {
            formattedPositions[key] = {
                x: Math.round(pos.x),
                y: Math.round(pos.y)
            };
        }
    
        // Format the output for easy copying
        let output = 'const fieldPositions = {\n';
        for (const [key, pos] of Object.entries(formattedPositions)) {
            output += `    "${key}": { x: ${pos.x}, y: ${pos.y} },\n`;
        }
        output += '};';
    
        console.log(output); // Log to console
        alert(output); // Show in an alert for easy copying
    }

    initializeCanvas() {
        this.canvas.width = 512;
        this.canvas.height = 400;
        console.log("Canvas initialized:", this.canvas.width, "x", this.canvas.height);
    }
    

    setupEventListeners() {
        const pathSelector = document.getElementById('pathSelector');
        if (!pathSelector) {
            console.error("Path selector not found");
            return;
        }

        pathSelector.addEventListener('change', (e) => {
            const matchNumber = e.target.value;
            if (matchNumber) {
                this.fetchPathData(matchNumber);
            }
        });

        const playButton = document.getElementById('playButton');
        const pauseButton = document.getElementById('pauseButton');
        const resetButton = document.getElementById('resetButton');

        if (playButton && pauseButton && resetButton) {
            playButton.addEventListener('click', () => this.play());
            pauseButton.addEventListener('click', () => this.pause());
            resetButton.addEventListener('click', () => this.reset());
        } else {
            console.error("One or more control buttons not found");
        }
    }

    fetchPathData(matchNumber) {
        const teamNumber = document.getElementById('team_number')?.value;
        const urlParams = new URLSearchParams(window.location.search);
        const compCode = urlParams.get('comp');

        if (!teamNumber || !compCode) {
            console.error("Missing team number or competition code");
            console.log("Team Number:", teamNumber);
            console.log("Competition Code:", compCode);
            return;
        }

        console.log(`Fetching path data for team ${teamNumber}, match ${matchNumber}`);

        fetch(`/api/get_path_data/${teamNumber}/?comp=${compCode}&match=${matchNumber}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received path data:", data);
            if (data.path) {
                this.currentPath = Array.isArray(data.path) ? data.path : JSON.parse(data.path);
                this.currentPath = this.currentPath.map(pos => String(pos).trim()).filter(pos => pos !== '');
                console.log("Processed path:", this.currentPath);
                this.reset();
            } else {
                console.error("No path data in response");
            }
        })
        .catch(error => {
            console.error('Error fetching path data:', error);
        });
    }

    play() {
        console.log("Play called");
        if (!this.isPlaying && this.currentPath.length > 0) {
            this.isPlaying = true;
            this.animate();
        }
    }

    pause() {
        console.log("Pause called");
        this.isPlaying = false;
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }

    reset() {
        console.log("Reset called");
        this.currentIndex = 0;
        this.pause();
        this.clearCanvas();
        this.drawPath();
        if (this.currentPath.length > 0) {
            this.drawRobot(this.currentPath[0]);
        }
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawPath() {
        if (!this.currentPath.length) return;

        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
        this.ctx.lineWidth = 2;

        this.currentPath.forEach((pos, index) => {
            if (fieldPositions[pos]) {
                if (index === 0) {
                    this.ctx.moveTo(fieldPositions[pos].x, fieldPositions[pos].y);
                } else {
                    this.ctx.lineTo(fieldPositions[pos].x, fieldPositions[pos].y);
                }
            }
        });
        this.ctx.stroke();

        // Draw points
        this.currentPath.forEach(pos => {
            if (fieldPositions[pos]) {
                this.ctx.beginPath();
                this.ctx.arc(fieldPositions[pos].x, fieldPositions[pos].y, 5, 0, 2 * Math.PI);
                this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
                this.ctx.fill();
            }
        });
    }

    drawRobot(position) {
        if (!fieldPositions[position]) return;

        // Draw robot
        this.ctx.beginPath();
        this.ctx.arc(fieldPositions[position].x, fieldPositions[position].y, 10, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'red';
        this.ctx.fill();

        // Draw direction line
        if (this.currentIndex < this.currentPath.length - 1) {
            const nextPos = fieldPositions[this.currentPath[this.currentIndex + 1]];
            if (nextPos) {
                this.ctx.beginPath();
                this.ctx.moveTo(fieldPositions[position].x, fieldPositions[position].y);
                this.ctx.lineTo(nextPos.x, nextPos.y);
                this.ctx.strokeStyle = 'red';
                this.ctx.lineWidth = 2;
                this.ctx.stroke();
            }
        }
    }

    animate() {
        if (!this.isPlaying) return;

        this.clearCanvas();
        this.drawPath();
        this.drawRobot(this.currentPath[this.currentIndex]);

        if (this.currentIndex < this.currentPath.length - 1) {
            this.currentIndex++;
            setTimeout(() => {
                this.animationFrame = requestAnimationFrame(() => this.animate());
            }, 1000);
        } else {
            this.isPlaying = false;
        }
    }
}

// Initialize when the page loads
if (window.replaySystemInitialized) {
    console.warn('Replay System already initialized');
} else {
    window.replaySystemInitialized = true;
    document.addEventListener('DOMContentLoaded', () => {
        console.log("DOM loaded, initializing Replay System");
        new ReplaySystem();
    });
}
