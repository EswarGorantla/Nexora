// Oil Spill Detection Dashboard - Working Version
// Global Setup
const canvas = document.getElementById('detectionCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 800;
canvas.height = 600;

let resultImage = null;
let satelliteFile = null;
let aisFile = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    drawPlaceholder();
});

// Event Listeners Setup
function initializeEventListeners() {
    setupFileUpload('satelliteUpload', 'satelliteInput', (file) => {
        satelliteFile = file;
        document.getElementById('satelliteFileName').textContent = file.name;
    });
    
    setupFileUpload('aisUpload', 'aisInput', (file) => {
        aisFile = file;
        document.getElementById('aisFileName').textContent = file.name;
    });
    
    document.getElementById('runDetection').addEventListener('click', runDetection);
    document.getElementById('demoMode').addEventListener('click', loadDemoOutput);
    document.getElementById('clearMap').addEventListener('click', clearMap);
}

// File Upload Utility
function setupFileUpload(boxId, inputId, callback) {
    const uploadBox = document.getElementById(boxId);
    const fileInput = document.getElementById(inputId);
    
    uploadBox.addEventListener('click', () => fileInput.click());
    
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('active');
    });
    
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('active');
    });
    
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('active');
        if (e.dataTransfer.files.length > 0) {
            callback(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            callback(e.target.files[0]);
        }
    });
}

// Canvas Drawing
function drawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (resultImage) {
        ctx.drawImage(resultImage, 0, 0, canvas.width, canvas.height);
    } else {
        drawPlaceholder();
    }
}

function drawPlaceholder() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '20px Segoe UI';
    ctx.fillText('Run Detection to see model results here', 180, 300);
}

// ===== MAIN DETECTION FUNCTION - FIXED =====
async function runDetection() {
    if (!satelliteFile) {
        alert('Please upload a satellite image first!');
        return;
    }
    
    // Show loading state
    alert('Running detection... Please wait.');
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('image', satelliteFile);
        
        // Fetch from backend
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Backend error: ${response.status}`);
        }
        
        // Get the JSON response
        const data = await response.json();
        
        // Load the result image
        const img = new Image();
        img.onload = function() {
            resultImage = img;
            drawCanvas();
            updateMetrics(data.statistics);
        };
        img.src = 'data:image/jpeg;base64,' + data.image;
        
    } catch (error) {
        console.error('Detection error:', error);
        alert('Error: ' + error.message + '\n\nMake sure Flask backend is running on port 5000!');
    }
}

// Update Dashboard Metrics
function updateMetrics(stats) {
    document.getElementById('spillArea').textContent = stats.spill_area_km2.toFixed(2) + ' km²';
    document.getElementById('confidence').textContent = stats.confidence + '%';
    document.getElementById('shipsCount').textContent = stats.pixel_count;
    document.getElementById('timestamp').textContent = stats.coverage_percentage + '%';
}

// Demo Mode
function loadDemoOutput() {
    alert('Demo mode: Using sample output');
    // You can add a demo image here if needed
}

// Clear Map
function clearMap() {
    resultImage = null;
    satelliteFile = null;
    aisFile = null;
    document.getElementById('satelliteFileName').textContent = '';
    document.getElementById('aisFileName').textContent = '';
    drawPlaceholder();
    
    // Reset metrics
    document.getElementById('spillArea').textContent = '-- km²';
    document.getElementById('confidence').textContent = '--%';
    document.getElementById('shipsCount').textContent = '--';
    document.getElementById('timestamp').textContent = '--%';
}
