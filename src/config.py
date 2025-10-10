"""
Configuration module for AI Emotion Tracking System
Contains all settings for video, audio processing, and emotion tracking
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Video settings
VIDEO_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30,
    'camera_index': 0,
    'backend': 'opencv',  # opencv backend for webcam
}

# Audio settings
AUDIO_CONFIG = {
    'sample_rate': 16000,  # Required for Wav2Vec2 model
    'channels': 1,  # Mono audio
    'chunk_duration': 1.0,  # Process 1 second chunks
    'chunk_size': 1024,
    'format': 'float32',
}

# Model settings
MODEL_CONFIG = {
    'video_model': 'deepface',  # Use DeepFace for facial emotion
    'audio_model': 'superb/wav2vec2-base-superb-er',  # Hugging Face emotion recognition model
    'video_backend': 'opencv',
    'use_mps': True,  # Use Apple MPS (Metal Performance Shaders) for M3
}

# Processing settings
PROCESSING_CONFIG = {
    'update_frequency': 0.1,  # Update every 0.1 seconds (real-time)
    'video_enabled': True,
    'audio_enabled': True,
    'temporal_smoothing_alpha': 0.6,  # Smoothing factor (0-1, balanced for stability)
    'min_face_confidence': 0.3,  # Minimum confidence for face detection
    'sensitivity_boost': 1.3,  # Amplify small changes (reduced to prevent maxing out)
    'emotion_decay_rate': 0.95,  # How much emotions persist (0.95 = 95% retained per update)
}

# Comprehensive emotion list (25-30 emotions)
EMOTION_LIST = [
    # Visual emotions (from DeepFace)
    'happy',
    'sad',
    'angry',
    'fear',
    'surprise',
    'disgust',
    'neutral',
    
    # Vocal emotions (from speech)
    'calm',
    'excited',
    'frustrated',
    'engaged',
    'confused',
    'anxious',
    'confident',
    'interested',
    'bored',
    'curious',
    'stressed',
    
    # Derived/composite emotions
    'receptiveness',  # Derived from engagement + positive emotions
    'awareness',      # Derived from attention indicators
    'trust',          # Derived from calm + happy
    'anticipation',   # Derived from excited + curious
    'relaxed',        # Derived from calm + neutral
    'skeptical',      # Derived from confused + neutral
    'distracted',     # Inverse of engaged
    'enthusiastic',   # Derived from excited + happy
    'contemplative',  # Derived from neutral + interested
    'alert',          # Derived from awareness + surprise
]

# Emotion fusion weights (video vs audio)
FUSION_WEIGHTS = {
    'video': 0.5,  # 50% weight for visual emotions
    'audio': 0.5,  # 50% weight for audio emotions
}

# Logging settings
LOGGING_CONFIG = {
    'log_file': LOGS_DIR / 'emotion_tracker.log',
    'error_log_file': LOGS_DIR / 'errors.log',
    'ui_log_file': LOGS_DIR / 'ui_client.log',
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Flask settings
FLASK_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'threaded': True,
}

# Performance optimization for M3
OPTIMIZATION_CONFIG = {
    'use_gpu': True,  # Use GPU acceleration
    'device': 'mps',  # Apple Metal Performance Shaders
    'num_threads': 4,  # Number of processing threads
    'batch_size': 1,   # Process one frame/chunk at a time for low latency
}

# Face Mesh settings (MediaPipe)
MESH_CONFIG = {
    'enabled': True,  # Enable face mesh overlay
    'color': (0, 255, 0),  # Green mesh (RGB)
    'thickness': 1,  # Line thickness
    'circle_radius': 1,  # Landmark point radius
    'show_landmarks': True,  # Show landmark points
    'show_connections': True,  # Show connecting lines
    'show_tesselation': True,  # Show full face tesselation
    'show_contours': True,  # Show face contours
    'show_irises': True,  # Show iris tracking
    'confidence_threshold': 0.3,  # Minimum detection confidence (lowered for sensitivity)
}

# OpenAI Chat Configuration
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY'),  # Load from environment variable
    'model': 'gpt-4o',  # GPT-4o for best emotional intelligence
    'max_tokens': 500,  # Reasonable response length
    'temperature': 0.8,  # Balanced creativity and consistency
    'rate_limit': 30,  # Max 30 messages per minute
    'max_history': 10,  # Keep last 10 messages for context
}

# Tone Override Options
TONE_OVERRIDES = {
    'auto': 'Automatically adapt tone based on detected emotions',
    'calming': 'Always use a calming and reassuring tone',
    'empathetic': 'Always use an empathetic and supportive tone',
    'enthusiastic': 'Always use an enthusiastic and celebratory tone',
    'professional': 'Always use a balanced and professional tone',
    'patient': 'Always use a clear and patient tone'
}


