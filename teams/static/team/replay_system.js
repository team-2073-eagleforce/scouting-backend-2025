console.log("Replay System Loading...");

const ORIGINAL_CANVAS_WIDTH = 512;
const ORIGINAL_CANVAS_HEIGHT = 400;

// Field position configurations
const fieldPositions = {
    "A": { x: 277, y: 170 },
    "B": { x: 279, y: 230 },
    "C": { x: 285, y: 288 },
    "D": { x: 331, y: 315 },
    "E": { x: 375, y: 315 },
    "F": { x: 419, y: 288 },
    "G": { x: 430, y: 220 },
    "H": { x: 430, y: 170 },
    "I": { x: 418, y: 105 },
    "J": { x: 374, y: 80 },
    "K": { x: 330, y: 80 },
    "L": { x: 284, y: 105 },
    "processor": { x: 388, y: 375 },
    "groundA": { x: 173, y: 110 },
    "groundB": { x: 176, y: 210 },
    "groundC": { x: 175, y: 300 },
    "sourceA": { x: 88, y: 120 },
    "sourceB": { x: 86, y: 300 },
};

class ReplaySystem {
    constructor() {
        console.log("Initializing Replay System");
        this.canvas = document.getElementById('replayCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentPath = ''; // Changed to empty string instead of array
        this.currentIndex = 0;
        this.isPlaying = false;
        this.animationFrame = null;

        this.currentPosition = { x: 0, y: 0 };
        this.targetPosition = { x: 0, y: 0 };
        this.animationProgress = 0;
        this.animationDuration = 1000; // Duration in milliseconds
        this.lastTimestamp = 0;

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

    getScaledPosition(position) {
        const scaleX = this.canvas.width / ORIGINAL_CANVAS_WIDTH;
        const scaleY = this.canvas.height / ORIGINAL_CANVAS_HEIGHT;
    
        return {
            x: position.x * scaleX,
            y: position.y * scaleY
        };
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
        const backButton = document.getElementById('backButton');
        const forwardButton = document.getElementById('forwardButton');
    
        if (playButton && pauseButton && resetButton && backButton && forwardButton) {
            playButton.addEventListener('click', () => this.play());
            pauseButton.addEventListener('click', () => this.pause());
            resetButton.addEventListener('click', () => this.reset());
            backButton.addEventListener('click', () => this.stepBack());
            forwardButton.addEventListener('click', () => this.stepForward());
        } else {
            console.error("One or more control buttons not found");
        }
    
        window.addEventListener('resize', () => {
            this.initializeCanvas();
            this.reset();
        });
    }

    drawCurrentPosition() {
        if (!this.currentPath) {
            console.log("No current path");
            return;
        }
    
        const positions = this.currentPath.split(',').map(pos => pos.trim());
        const currentPos = positions[this.currentIndex];
        const nextPos = positions[this.currentIndex + 1];
    
        console.log("Drawing position:", currentPos);
        console.log("Next position:", nextPos);
        console.log("Field position data:", fieldPositions[currentPos]);
    
        if (!fieldPositions[currentPos]) {
            console.error("Invalid current position:", currentPos);
            return;
        }
    
        // Draw current position
        const scaledCurrentPos = this.getScaledPosition(fieldPositions[currentPos]);
        this.ctx.beginPath();
        this.ctx.arc(scaledCurrentPos.x, scaledCurrentPos.y, 5, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        this.ctx.fill();
    
        // Draw line to next position if it exists
        if (nextPos && fieldPositions[nextPos]) {
            const scaledNextPos = this.getScaledPosition(fieldPositions[nextPos]);
            this.ctx.beginPath();
            this.ctx.moveTo(scaledCurrentPos.x, scaledCurrentPos.y);
            this.ctx.lineTo(scaledNextPos.x, scaledNextPos.y);
            this.ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
    
            // Draw next position
            this.ctx.beginPath();
            this.ctx.arc(scaledNextPos.x, scaledNextPos.y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
            this.ctx.fill();
        }
    }    

    animate(timestamp) {
        if (!this.isPlaying) return;
    
        if (!this.lastTimestamp) {
            this.lastTimestamp = timestamp;
        }
    
        const deltaTime = timestamp - this.lastTimestamp;
        this.lastTimestamp = timestamp;
    
        // Update animation progress
        this.animationProgress += deltaTime;
        
        const positions = this.currentPath.split(',');
        const currentPos = fieldPositions[positions[this.currentIndex]];
        const nextPos = fieldPositions[positions[this.currentIndex + 1]];
    
        if (currentPos && nextPos) {
            // Calculate interpolation factor (0 to 1)
            const t = Math.min(this.animationProgress / this.animationDuration, 1);
            
            // Interpolate between positions
            const scaledCurrentPos = this.getScaledPosition(currentPos);
            const scaledNextPos = this.getScaledPosition(nextPos);
            
            const interpolatedX = scaledCurrentPos.x + (scaledNextPos.x - scaledCurrentPos.x) * t;
            const interpolatedY = scaledCurrentPos.y + (scaledNextPos.y - scaledCurrentPos.y) * t;
    
            // Clear and redraw
            this.clearCanvas();
            
            // Draw path line
            this.ctx.beginPath();
            this.ctx.moveTo(scaledCurrentPos.x, scaledCurrentPos.y);
            this.ctx.lineTo(scaledNextPos.x, scaledNextPos.y);
            this.ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
    
            // Draw points
            this.ctx.beginPath();
            this.ctx.arc(scaledCurrentPos.x, scaledCurrentPos.y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
            this.ctx.fill();
    
            this.ctx.beginPath();
            this.ctx.arc(scaledNextPos.x, scaledNextPos.y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
            this.ctx.fill();
    
            // Draw robot at interpolated position
            this.ctx.beginPath();
            this.ctx.arc(interpolatedX, interpolatedY, 10, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'red';
            this.ctx.fill();
    
            // Move to next position when animation completes
            if (t === 1) {
                this.currentIndex++;
                this.animationProgress = 0;
                this.lastTimestamp = 0;
            }
        }
    
        this.updatePositionDisplay();
    
        // Continue animation if there are more positions
        if (this.currentIndex < this.currentPath.split(',').length - 1) {
            this.animationFrame = requestAnimationFrame((timestamp) => this.animate(timestamp));
        } else {
            this.isPlaying = false;
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
                // Clean up the path string by removing extra spaces after commas
                this.currentPath = data.path.split(',').map(pos => pos.trim()).join(',');
                console.log("Path loaded:", this.currentPath);
                this.reset();
            } else {
                console.error("No path data in response");
            }
        })
        .catch(error => {
            console.error('Error fetching path data:', error);
        });
    }      
    
    updatePositionDisplay() {
        const currentPosition = document.getElementById('currentPosition');
        const totalPositions = document.getElementById('totalPositions');
        if (currentPosition && totalPositions && this.currentPath) {
            const positions = this.currentPath.split(',');
            currentPosition.textContent = this.currentIndex + 1;
            totalPositions.textContent = positions.length;
        }
    }

    play() {
        console.log("Play called");
        if (!this.isPlaying && this.currentPath) {
            const positions = this.currentPath.split(',');
            if (this.currentIndex < positions.length - 1) {
                this.isPlaying = true;
                this.lastTimestamp = 0;
                this.animationProgress = 0;
                this.animate(performance.now());
            }
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
        this.drawCurrentPosition();
        this.updatePositionDisplay();
    }

    stepBack() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.clearCanvas();
            this.drawCurrentPosition();
            this.updatePositionDisplay();
        }
    }

    stepForward() {
        const positions = this.currentPath.split(',');
        if (this.currentIndex < positions.length - 1) {
            this.currentIndex++;
            this.clearCanvas();
            this.drawCurrentPosition();
            this.updatePositionDisplay();
        }
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

if (window.replaySystemInitialized) {
    console.warn('Replay System already initialized');
} else {
    window.replaySystemInitialized = true;
    document.addEventListener('DOMContentLoaded', () => {
        console.log("DOM loaded, initializing Replay System");
        new ReplaySystem();
    });
}
