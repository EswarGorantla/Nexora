from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from oil_spill_detector import detect_oil_spill_production
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Oil Spill Detection API',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API running'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'success': False, 'error': 'Invalid image'}), 400
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = detect_oil_spill_production(img_rgb)
        results['timestamp'] = datetime.now().isoformat()
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
