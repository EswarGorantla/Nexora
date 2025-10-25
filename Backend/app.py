from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import cv2
import io
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "Backend is running"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get uploaded image
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files['image']
        
        # Read image
        img = Image.open(file.stream).convert('RGB')
        img_array = np.array(img)
        
        # Resize for processing
        img_resized = cv2.resize(img_array, (800, 600))
        
        # Create grayscale for edge detection
        gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
        
        # Edge detection (simulating oil spill detection)
        edges = cv2.Canny(gray, 50, 150)
        
        # Create mask (1 where edges detected, 0 elsewhere)
        mask = (edges > 0).astype(np.uint8)
        
        # Create red overlay
        overlay = img_resized.copy()
        overlay[mask == 1] = [239, 68, 68]  # Red color for detected areas
        
        # Blend original and overlay
        result = cv2.addWeighted(img_resized, 0.7, overlay, 0.3, 0)
        
        # Calculate statistics
        total_pixels = mask.shape[0] * mask.shape[1]
        spill_pixels = np.sum(mask)
        coverage_percentage = (spill_pixels / total_pixels) * 100
        
        # Convert to km² (assuming each pixel = 100m²)
        spill_area_km2 = (spill_pixels * 100) / 1_000_000
        
        statistics = {
            "spill_area_km2": round(spill_area_km2, 2),
            "confidence": 87,  # Simulated confidence
            "pixel_count": int(spill_pixels),
            "coverage_percentage": round(coverage_percentage, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Convert result image to base64
        result_pil = Image.fromarray(result)
        buffer = io.BytesIO()
        result_pil.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "image": img_base64,
            "statistics": statistics
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Oil Spill Detection Backend Starting...")
    print("=" * 50)
    print("Backend: http://127.0.0.1:5000")
    print("Health Check: http://127.0.0.1:5000/health")
    print("Prediction Endpoint: http://127.0.0.1:5000/predict")
    print("=" * 50)
    app.run(debug=True, port=5000)
