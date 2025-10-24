from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,ngrok-skip-browser-warning')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('ngrok-skip-browser-warning', 'true')
    return response

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'running',
        'message': 'Oil Spill Detection API',
        'endpoints': ['/predict', '/health']
    })

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({'status': 'healthy', 'message': 'Backend is running properly'})

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print('📥 Received prediction request')
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        print(f'📁 File: {file.filename}')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f'💾 Saved to: {filepath}')
            
            # Handle AIS file if provided
            if 'ais' in request.files:
                ais_file = request.files['ais']
                if ais_file.filename != '':
                    ais_filename = secure_filename(ais_file.filename)
                    ais_filepath = os.path.join(app.config['UPLOAD_FOLDER'], ais_filename)
                    ais_file.save(ais_filepath)
                    print(f'💾 AIS file saved: {ais_filepath}')
            
            # TODO: Add your ML model prediction here
            # For now, return mock data
            
            print('✅ Processing complete, returning results')
            
            result = {
                'status': 'success',
                'message': 'Detection completed',
                'spill_area': '2.5 km²',
                'confidence': '87%',
                'pixels': '1,250',
                'spill_percentage': '3.2%',
                'detected_spills': 1,
                'risk_level': 'moderate'
            }
            
            return jsonify(result), 200
            
            # ALTERNATIVE: If you want to return an image instead:
            # from PIL import Image
            # import io
            # img = Image.open(filepath)
            # # Process with your model here
            # output = io.BytesIO()
            # img.save(output, format='PNG')
            # output.seek(0)
            # return send_file(output, mimetype='image/png')
        
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Flask Backend Starting...")
    print("=" * 60)
    print("📍 Local: http://localhost:5000")
    print("📍 Network: http://0.0.0.0:5000")
    print("=" * 60)
    print("\n✅ Endpoints available:")
    print("   GET  /         - API info")
    print("   GET  /health   - Health check")
    print("   POST /predict  - Run detection")
    print("\n🔧 Ready to accept requests!\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
