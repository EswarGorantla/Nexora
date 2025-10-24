from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from oil_spill_detector import detect_oil_spill_production
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Oil Spill Detection API',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'Health check',
            '/predict': 'POST - Upload image for detection'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API is running'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        # Read image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'error': 'Invalid image format'}), 400
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Run detection
        results = detect_oil_spill_production(img_rgb)
        
        # Add timestamp
        from datetime import datetime
        results['timestamp'] = datetime.now().isoformat()
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log for debugging
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
