// Oil Spill Detection Dashboard - WORKING VERSION
const canvas = document.getElementById('detectionCanvas');
const ctx = canvas.getContext('2d');
canvas.width = 800;
canvas.height = 600;

let resultImage = null;
let satelliteFile = null;
let aisFile = null;

// ⚠️ UPDATE THIS WITH YOUR CURRENT NGROK URL ⚠️
const BACKEND_URL = 'https://chang-nonpersonal-barrie.ngrok-free.dev';

console.log('🔧 Backend URL:', BACKEND_URL);

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Dashboard loaded');
    initializeEventListeners();
    drawPlaceholder();
    testBackendConnection();
});

// Test backend connection on load
async function testBackendConnection() {
    try {
        const response = await fetch(`${BACKEND_URL}/health`, {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': 'true'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connected:', data.message);
        } else {
            console.error('❌ Backend returned error:', response.status);
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error.message);
        console.log('📋 Checklist:');
        console.log('  1. Is Flask running? (python app.py)');
        console.log('  2. Is Ngrok running? (ngrok http 5000)');
        console.log('  3. Is BACKEND_URL correct in script2.js?');
        console.log('  4. Current BACKEND_URL:', BACKEND_URL);
    }
}

// Event Listeners
function initializeEventListeners() {
    setupFileUpload('satelliteUpload', 'satelliteInput', (file) => {
        satelliteFile = file;
        document.getElementById('satelliteFileName').textContent = file.name;
        console.log('📁 Satellite file:', file.name);
    });
    
    setupFileUpload('aisUpload', 'aisInput', (file) => {
        aisFile = file;
        document.getElementById('aisFileName').textContent = file.name;
        console.log('📁 AIS file:', file.name);
    });
    
    document.getElementById('runDetection').addEventListener('click', runDetection);
    document.getElementById('demoMode').addEventListener('click', loadDemoOutput);
    document.getElementById('clearMap').addEventListener('click', clearMap);
}

// File Upload
function setupFileUpload(boxId, inputId, callback) {
    const uploadBox = document.getElementById(boxId);
    const fileInput = document.getElementById(inputId);
    
    if (!uploadBox || !fileInput) {
        console.error('❌ Upload elements not found:', boxId, inputId);
        return;
    }
    
    uploadBox.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });
    
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('active');
    });
    
    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
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
    ctx.textAlign = 'center';
    ctx.fillText('Run Detection to see model results here', 400, 300);
}

// Run Detection
async function runDetection(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    console.log('🚀 Starting detection...');
    
    if (!satelliteFile) {
        alert('❌ Please upload a satellite image first!');
        return;
    }
    
    const btn = document.getElementById('runDetection');
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '⏳ Processing...';
    btn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('image', satelliteFile);
        
        if (aisFile) {
            formData.append('ais', aisFile);
        }
        
        console.log('📤 Sending to:', `${BACKEND_URL}/predict`);
        console.log('📦 Files:', satelliteFile.name, aisFile ? aisFile.name : 'No AIS');
        
        const response = await fetch(`${BACKEND_URL}/predict`, {
            method: 'POST',
            body: formData,
            headers: {
                'ngrok-skip-browser-warning': 'true'
            }
        });
        
        console.log('📥 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        console.log('📋 Content type:', contentType);
        
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            console.log('✅ Received data:', data);
            
            // Update metrics
            document.getElementById('spillArea').textContent = data.spill_area || '--';
            document.getElementById('confidence').textContent = data.confidence || '--';
            document.getElementById('shipsCount').textContent = data.pixels || '--';
            document.getElementById('timestamp').textContent = data.spill_percentage || '--';
            
            alert('✅ Detection completed successfully!\n\nSpill Area: ' + data.spill_area + '\nConfidence: ' + data.confidence);
            
        } else if (contentType && contentType.includes('image')) {
            const blob = await response.blob();
            console.log('🖼️ Received image, size:', blob.size);
            
            const img = new Image();
            img.onload = function() {
                resultImage = img;
                drawCanvas();
                console.log('✅ Image displayed on canvas');
                alert('✅ Detection completed! Check the map for results.');
            };
            
            img.onerror = function() {
                throw new Error('Failed to load result image');
            };
            
            img.src = URL.createObjectURL(blob);
        }
        
    } catch (error) {
        console.error('❌ Detection failed:', error);
        
        let errorMsg = '❌ Error: Failed to fetch\n\n';
        errorMsg += 'Make sure:\n';
        errorMsg += '1. Flask backend is running\n';
        errorMsg += '2. Ngrok is running\n';
        errorMsg += '3. BACKEND_URL in script2.js matches your ngrok URL\n\n';
        errorMsg += 'Current BACKEND_URL: ' + BACKEND_URL + '\n\n';
        errorMsg += 'Error details: ' + error.message;
        
        alert(errorMsg);
    } finally {
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    }
}

// Demo Mode
function loadDemoOutput(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    console.log('🎭 Loading demo mode');
    
    document.getElementById('spillArea').textContent = '2.5 km²';
    document.getElementById('confidence').textContent = '87%';
    document.getElementById('shipsCount').textContent = '1,250';
    document.getElementById('timestamp').textContent = '3.2%';
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#e0f2fe';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = 'rgba(239, 68, 68, 0.6)';
    ctx.beginPath();
    ctx.ellipse(400, 300, 150, 100, 0, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.fillStyle = '#1e293b';
    ctx.font = 'bold 24px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText('🎭 DEMO MODE', 400, 100);
    ctx.font = '16px Segoe UI';
    ctx.fillText('Simulated Oil Spill Detection', 400, 130);
    
    alert('✅ Demo mode loaded!');
}

// Clear Map
function clearMap(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    console.log('🧹 Clearing map');
    
    resultImage = null;
    satelliteFile = null;
    aisFile = null;
    
    document.getElementById('satelliteFileName').textContent = '';
    document.getElementById('aisFileName').textContent = '';
    document.getElementById('spillArea').textContent = '--';
    document.getElementById('confidence').textContent = '--';
    document.getElementById('shipsCount').textContent = '--';
    document.getElementById('timestamp').textContent = '--';
    
    document.getElementById('satelliteInput').value = '';
    document.getElementById('aisInput').value = '';
    
    drawPlaceholder();
}

console.log('✅ Script loaded successfully');
