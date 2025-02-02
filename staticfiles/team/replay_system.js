// Define field positions
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

function ReplaySystem() {
    var self = this;
    this.canvas = document.getElementById('replayCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.currentPath = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.animationFrame = null;

    console.log("ReplaySystem initialized");

    // Match canvas size to image
    var img = document.querySelector("img[alt='Auto Map']");
    if (img) {
        console.log("Found image, setting canvas size to:", img.width, "x", img.height);
        this.canvas.width = img.width;
        this.canvas.height = img.height;
    } else {
        console.error("Could not find Auto Map image");
    }

    this.setupEventListeners();
}

ReplaySystem.prototype.setupEventListeners = function() {
    var self = this;
    
    document.getElementById('pathSelector').addEventListener('change', function(e) {
        var selectedPath = e.target.value;
        console.log("Raw selected path:", selectedPath);
        
        try {
            // Handle different possible formats
            let pathArray;
            if (Array.isArray(selectedPath)) {
                pathArray = selectedPath;
            } else if (typeof selectedPath === 'string') {
                // Try parsing as JSON first
                try {
                    pathArray = JSON.parse(selectedPath);
                } catch (e) {
                    // If not valid JSON, try splitting by comma
                    pathArray = selectedPath.split(',');
                }
            }

            // Clean up the array
            self.currentPath = pathArray.map(function(pos) {
                return String(pos).trim();
            }).filter(function(pos) {
                return pos !== '';
            });

            console.log("Processed path array:", self.currentPath);
            
            if (self.currentPath.length > 0) {
                self.reset();
            }
        } catch (e) {
            console.error("Error processing path:", e);
            console.error("Raw path value:", selectedPath);
        }
    });

    document.getElementById('playButton').addEventListener('click', function() {
        console.log("Play button clicked");
        self.play();
    });

    document.getElementById('pauseButton').addEventListener('click', function() {
        console.log("Pause button clicked");
        self.pause();
    });

    document.getElementById('resetButton').addEventListener('click', function() {
        console.log("Reset button clicked");
        self.reset();
    });
};

ReplaySystem.prototype.play = function() {
    if (!this.isPlaying) {
        this.isPlaying = true;
        this.animate();
    }
};

ReplaySystem.prototype.pause = function() {
    this.isPlaying = false;
    if (this.animationFrame) {
        cancelAnimationFrame(this.animationFrame);
    }
};

ReplaySystem.prototype.reset = function() {
    this.currentIndex = 0;
    this.pause();
    this.clearCanvas();
    this.drawPath();
    if (this.currentPath.length > 0) {
        this.drawRobot(this.currentPath[0]);
    }
};

ReplaySystem.prototype.clearCanvas = function() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
};

ReplaySystem.prototype.drawPath = function() {
    if (this.currentPath.length === 0) return;

    // Draw lines connecting all points
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

    // Draw points at each position
    this.currentPath.forEach(pos => {
        if (fieldPositions[pos]) {
            this.ctx.beginPath();
            this.ctx.arc(fieldPositions[pos].x, fieldPositions[pos].y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
            this.ctx.fill();
        }
    });
};

ReplaySystem.prototype.drawRobot = function(position) {
    if (!fieldPositions[position]) return;

    // Draw the robot as a red dot
    this.ctx.beginPath();
    this.ctx.arc(fieldPositions[position].x, fieldPositions[position].y, 10, 0, 2 * Math.PI);
    this.ctx.fillStyle = 'red';
    this.ctx.fill();

    // Draw direction line to next position if available
    if (this.currentIndex < this.currentPath.length - 1) {
        var nextPos = fieldPositions[this.currentPath[this.currentIndex + 1]];
        if (nextPos) {
            this.ctx.beginPath();
            this.ctx.moveTo(fieldPositions[position].x, fieldPositions[position].y);
            this.ctx.lineTo(nextPos.x, nextPos.y);
            this.ctx.strokeStyle = 'red';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        }
    }
};

ReplaySystem.prototype.animate = function() {
    var self = this;
    if (!this.isPlaying) return;

    this.clearCanvas();
    this.drawPath();
    this.drawRobot(this.currentPath[this.currentIndex]);

    if (this.currentIndex < this.currentPath.length - 1) {
        this.currentIndex++;
        setTimeout(function() {
            self.animationFrame = requestAnimationFrame(function() { self.animate(); });
        }, 1000);
    } else {
        this.isPlaying = false;
    }
};

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing ReplaySystem");
    var replaySystem = new ReplaySystem();
});
