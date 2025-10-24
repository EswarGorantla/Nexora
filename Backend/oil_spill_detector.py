import cv2
import numpy as np
import base64
from PIL import Image

def detect_oil_spill_production(image_input):
    """Oil spill detection function"""
    
    # Handle different input types
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif isinstance(image_input, np.ndarray):
        img_rgb = image_input
        if len(img_rgb.shape) == 2:
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_GRAY2RGB)
    elif isinstance(image_input, Image.Image):
        img_rgb = np.array(image_input.convert('RGB'))
    else:
        raise ValueError("Invalid image input")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (11, 11), 0)
    
    # Dark region detection
    threshold = np.percentile(blur, 20)
    dark = (blur < threshold).astype(np.uint8) * 255
    
    # Morphological operations
    kernel = np.ones((5, 5), np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, kernel)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(dark)
    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            cv2.drawContours(mask, [cnt], -1, 255, -1)
    
    # Calculate metrics
    spill_pixels = np.count_nonzero(mask)
    coverage = (spill_pixels / mask.size) * 100
    
    if spill_pixels > 0:
        dark_values = gray[mask > 0]
        avg_darkness = float(np.mean(dark_values))
        confidence = (100 - avg_darkness) / 100.0
        confidence = max(0.3, min(0.95, confidence))
    else:
        confidence = 0.0
    
    area_km2 = (spill_pixels * 100) / 1_000_000
    detected = (coverage > 0.5) and (confidence > 0.35) and (area_km2 > 0.3)
    
    # Create visualization
    overlay = img_rgb.copy()
    overlay[mask > 0] = [255, 0, 0]
    blended = cv2.addWeighted(img_rgb, 0.7, overlay, 0.3, 0)
    
    # Encode result image
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(blended, cv2.COLOR_RGB2BGR))
    result_img_b64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        'success': True,
        'spill_detected': bool(detected),
        'confidence': round(float(confidence), 3),
        'coverage_percent': round(float(coverage), 2),
        'area_km2': round(float(area_km2), 4),
        'num_pixels': int(spill_pixels),
        'result_image': f"data:image/jpeg;base64,{result_img_b64}",
        'status': 'HIGH RISK' if (detected and confidence > 0.7) else 'MODERATE RISK' if detected else 'NO RISK',
        'message': 'Oil spill detected!' if detected else 'No oil spill detected'
    }
