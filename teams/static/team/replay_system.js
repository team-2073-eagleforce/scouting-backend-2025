console.log("Replay System Loading...");

// Field position configurations
const fieldPositions = {
    "A": { x: 50, y: 50 },
    "B": { x: 100, y: 100 },
    "C": { x: 150, y: 150 },
    "D": { x: 200, y: 200 },
    "E": { x: 250, y: 250 },
    "F": { x: 300, y: 300 },
    "H": { x: 350, y: 350 },
    "G": { x: 400, y: 400 },
    "processor": { x: 450, y: 450 },
    "groundA": { x: 500, y: 500 },
    "groundB": { x: 550, y: 550 },
    "groundC": { x: 600, y: 600 },
    "sourceA": { x: 650, y: 650 },
    "sourceB": { x: 700, y: 700 }
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
    }

    initializeCanvas() {
        const img = document.querySelector("img[alt='Auto Map']");
        if (img) {
            this.canvas.width = img.width;
            this.canvas.height = img.height;
            console.log("Canvas initialized:", this.canvas.width, "x", this.canvas.height);
        } else {
            console.error("Auto Map image not found");
        }
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
