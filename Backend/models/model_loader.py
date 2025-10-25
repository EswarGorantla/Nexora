import os
import tensorflow as tf
from tensorflow import keras
import torch

# Global variable to cache loaded model
_MODEL_CACHE = None

def load_model(model_path='model/weights.h5', framework='tensorflow'):
    """
    Load your trained model (cached to avoid reloading)
    
    Args:
        model_path: Path to model weights
        framework: 'tensorflow', 'pytorch', or 'onnx'
    
    Returns:
        Loaded model object
    """
    global _MODEL_CACHE
    
    if _MODEL_CACHE is not None:
        print("📦 Using cached model")
        return _MODEL_CACHE
    
    print(f"🔄 Loading model from {model_path}...")
    
    if framework == 'tensorflow':
        # TensorFlow/Keras model
        _MODEL_CACHE = keras.models.load_model(model_path, compile=False)
        
    elif framework == 'pytorch':
        # PyTorch model
        import torch
        _MODEL_CACHE = torch.load(model_path)
        _MODEL_CACHE.eval()
        
    elif framework == 'onnx':
        # ONNX model
        import onnxruntime as ort
        _MODEL_CACHE = ort.InferenceSession(model_path)
    
    else:
        raise ValueError(f"Unknown framework: {framework}")
    
    print("✅ Model loaded successfully")
    return _MODEL_CACHE


# ============================================
# 🔴 OPTION A: If your model is in Colab
# ============================================
def load_model_from_colab_code():
    """
    If you can't export weights, recreate your model architecture here
    and load weights separately
    """
    from tensorflow.keras import layers, models
    
    # Example: U-Net architecture (REPLACE WITH YOUR ARCHITECTURE)
    def unet_model(input_shape=(256, 256, 3)):
        inputs = layers.Input(shape=input_shape)
        
        # Encoder
        c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
        c1 = layers.Conv2D(64, 3, activation='relu', padding='same')(c1)
        p1 = layers.MaxPooling2D((2, 2))(c1)
        
        c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(p1)
        c2 = layers.Conv2D(128, 3, activation='relu', padding='same')(c2)
        p2 = layers.MaxPooling2D((2, 2))(c2)
        
        # Bottleneck
        c3 = layers.Conv2D(256, 3, activation='relu', padding='same')(p2)
        
        # Decoder
        u2 = layers.UpSampling2D((2, 2))(c3)
        u2 = layers.concatenate([u2, c2])
        c4 = layers.Conv2D(128, 3, activation='relu', padding='same')(u2)
        
        u1 = layers.UpSampling2D((2, 2))(c4)
        u1 = layers.concatenate([u1, c1])
        c5 = layers.Conv2D(64, 3, activation='relu', padding='same')(u1)
        
        outputs = layers.Conv2D(1, 1, activation='sigmoid')(c5)
        
        return models.Model(inputs, outputs)
    
    model = unet_model()
    # Load weights if you have them
    # model.load_weights('model/weights.h5')
    
    return model
