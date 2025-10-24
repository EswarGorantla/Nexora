/**
 * Oil Spill Detection Dashboard - Simplified Version
 * Center map shows ONLY the result image from detection,
 * not the uploaded SAR or AIS inputs.
 */

// ===============================
// Global Setup
// ===============================
const canvas = document.getElementById("detectionCanvas");
const ctx = canvas.getContext("2d");
canvas.width = 800;
canvas.height = 600;

let resultImage = null; // The ML output image
let satelliteFile = null;
let aisFile = null;

// ===============================
// Initialization
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners();
  drawPlaceholder();
});

// ===============================
// Event Listeners Setup
// ===============================
function initializeEventListeners() {
  setupFileUpload("satelliteUpload", "satelliteInput", (file) => {
    satelliteFile = file;
    document.getElementById("satelliteFileName").textContent = `✓ ${file.name}`;
  });

  setupFileUpload("aisUpload", "aisInput", (file) => {
    aisFile = file;
    document.getElementById("aisFileName").textContent = `✓ ${file.name}`;
  });

  document.getElementById("runDetection").addEventListener("click", runDetection);
  document.getElementById("demoMode").addEventListener("click", loadDemoOutput);
  document.getElementById("clearMap").addEventListener("click", clearMap);
}

// ===============================
// File Upload Utility
// ===============================
function setupFileUpload(boxId, inputId, callback) {
  const uploadBox = document.getElementById(boxId);
  const fileInput = document.getElementById(inputId);

  uploadBox.addEventListener("click", () => fileInput.click());
  uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.classList.add("active");
  });
  uploadBox.addEventListener("dragleave", () => uploadBox.classList.remove("active"));
  uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.classList.remove("active");
    if (e.dataTransfer.files.length > 0) {
      callback(e.dataTransfer.files[0]);
    }
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      callback(e.target.files[0]);
    }
  });
}

// ===============================
// Canvas Drawing (Only Result)
// ===============================
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
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#94a3b8";
  ctx.font = "20px Segoe UI";
  ctx.fillText("Run Detection to see model results here", 180, 300);
}

// ===============================
// Buttons: Run Detection, Demo, Clear
// ===============================
async function runDetection() {
  if (!satelliteFile) {
    alert("Please upload a satellite image first!");
    return;
  }

  alert("Running detection... (this will fetch your ML output)");

  // When backend is ready, uncomment this block:
  /*
  const formData = new FormData();
  formData.append("image", satelliteFile);
  if (aisFile) formData.append("ais", aisFile);

  const res = await fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    body: formData,
  });

  const blob = await res.blob();
  const img = new Image();
  img.onload = function () {
    resultImage = img;
    drawCanvas();
  };
  img.src = URL.createObjectURL(blob);
  */

  // For now, simulate with demo
  loadDemoOutput();
}

function loadDemoOutput() {
  // Use a sample output image (replace path with your output)
  const img = new Image();
  img.onload = function () {
    resultImage = img;
    drawCanvas();
  };
  img.src = "demo_result.jpg"; // <-- Replace this with your real result image filename
}

function clearMap() {
  resultImage = null;
  satelliteFile = null;
  aisFile = null;
  document.getElementById("satelliteFileName").textContent = "";
  document.getElementById("aisFileName").textContent = "";
  drawPlaceholder();
}
