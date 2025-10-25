import numpy as np
from PIL import Image
import io

from .model_loader import load_model

# ============================================
# IMAGE PREPROCESSING
# ============================================

def preprocess_image(image_path, target_size=(256, 256)):
    """
    Load and preprocess image for model input
    
    Args:
        image_path: Path to image file
        target_size: Target size for model (height, width)
    
    Returns:
        preprocessed: Preprocessed numpy array ready for model
        original: Original PIL Image (for overlay later)
    """
    # Load image
    img = Image.open(image_path).convert('RGB')
    original_img = img.copy()
    
    # Resize
    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    img_array = np.array(img_resized, dtype=np.float32)
    
    # Normalize to [0, 1] (adjust based on your training)
    img_array = img_array / 255.0
    
    # Add batch dimension: (H, W, C) -> (1, H, W, C)
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array, original_img


# ============================================
# MODEL PREDICTION
# ============================================

def predict_mask(model, preprocessed_image):
    """
    Run model inference
    
    Args:
        model: Loaded model object
        preprocessed_image: Preprocessed numpy array
    
    Returns:
        mask: Binary mask (H x W) with 1=spill, 0=no-spill
    """
    # Run prediction
    prediction = model.predict(preprocessed_image, verbose=0)
    
    # prediction shape: (1, H, W, 1) or (1, H, W, num_classes)
    pred_squeeze = np.squeeze(prediction)  # Remove batch and channel dims
    
    # Threshold to binary mask
    threshold = 0.5  # Adjust based on your model
    mask = (pred_squeeze > threshold).astype(np.uint8)
    
    return mask


# ============================================
# POSTPROCESSING
# ============================================

def postprocess_mask(mask, original_size):
    """
    Resize mask back to original image size and clean up
    
    Args:
        mask: Binary mask from model (model_h x model_w)
        original_size: (width, height) of original image
    
    Returns:
        mask_resized: Mask resized to original dimensions
    """
    from PIL import Image
    
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))
    mask_resized = mask_img.resize(original_size, Image.Resampling.NEAREST)
    mask_resized = (np.array(mask_resized) > 127).astype(np.uint8)
    
    # Optional: morphological operations to clean up mask
    # from scipy.ndimage import binary_opening, binary_closing
    # mask_resized = binary_closing(mask_resized, structure=np.ones((5,5)))
    # mask_resized = binary_opening(mask_resized, structure=np.ones((3,3)))
    
    return mask_resized


# ============================================
# VISUALIZATION
# ============================================

def create_overlay(original_img, mask, color=(239, 68, 68), alpha=0.5):
    """
    Create visualization with mask overlaid on original image
    
    Args:
        original_img: PIL Image
        mask: Binary mask (same size as image)
        color: RGB color for overlay
        alpha: Transparency (0=invisible, 1=opaque)
    
    Returns:
        overlay_img: PIL Image with overlay
    """
    # Convert to numpy
    img_array = np.array(original_img)
    
    # Create colored overlay
    overlay = np.zeros_like(img_array)
    overlay[mask == 1] = color
    
    # Blend
    blended = img_array.astype(float) * (1 - alpha * mask[..., None]) + \
              overlay.astype(float) * (alpha * mask[..., None])
    blended = blended.clip(0, 255).astype(np.uint8)
    
    return Image.fromarray(blended)


# ============================================
# STATISTICS CALCULATION
# ============================================

def calculate_statistics(mask, pixel_resolution_m=10):
    """
    Calculate spill statistics from mask
    
    Args:
        mask: Binary mask
        pixel_resolution_m: Resolution in meters (e.g., 10m for Sentinel-1)
    
    Returns:
        stats: Dictionary of statistics
    """
    spill_pixels = int(np.sum(mask))
    total_pixels = mask.size
    spill_percentage = round(100.0 * spill_pixels / max(1, total_pixels), 3)
    
    # Calculate area in km²
    pixel_area_m2 = pixel_resolution_m ** 2
    spill_area_m2 = spill_pixels * pixel_area_m2
    spill_area_km2 = round(spill_area_m2 / 1e6, 3)
    
    # Estimate confidence (you can use model's confidence scores)
    confidence = round(min(95, 50 + spill_percentage * 10), 2)
    
    stats = {
        "spill_area_px": spill_pixels,
        "spill_area_km2": spill_area_km2,
        "image_pixels": total_pixels,
        "spill_percentage": spill_percentage,
        "confidence": confidence,
        "image_width": mask.shape[1],
        "image_height": mask.shape[0],
        "vessels_nearby": []
    }
    
    return stats


# ============================================
# MAIN INFERENCE PIPELINE
# ============================================

def run_oil_spill_detection(image_path, ais_path=None):
    """
    Complete pipeline: load image → predict → create overlay → calculate stats
    
    Args:
        image_path: Path to satellite image
        ais_path: Path to AIS data (optional)
    
    Returns:
        png_bytes: PNG image with overlay
        stats: Dictionary of statistics
    """
    # Load model (cached)
    model = load_model(model_path='model/weights.h5', framework='tensorflow')
    
    # Preprocess
    preprocessed, original_img = preprocess_image(image_path, target_size=(256, 256))
    
    # Predict
    mask = predict_mask(model, preprocessed)
    
    # Postprocess
    original_size = original_img.size  # (width, height)
    mask_full = postprocess_mask(mask, original_size)
    
    # Create overlay
    overlay_img = create_overlay(original_img, mask_full, color=(239, 68, 68), alpha=0.5)
    
    # Calculate statistics
    stats = calculate_statistics(mask_full, pixel_resolution_m=10)
    
    # Convert to PNG bytes
    with io.BytesIO() as buffer:
        overlay_img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
    
    return png_bytes, stats
