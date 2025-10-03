"""
Audio Processing Module for Speech Emotion Recognition
Uses PyAudio for audio capture and Wav2Vec2 for emotion detection
"""

import pyaudio
import numpy as np
import threading
import time
import logging
import torch
from typing import Dict, Optional
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
from config import AUDIO_CONFIG, MODEL_CONFIG, PROCESSING_CONFIG, LOGGING_CONFIG, OPTIMIZATION_CONFIG

# Setup logging
logging.basicConfig(
    filename=LOGGING_CONFIG['log_file'],
    level=LOGGING_CONFIG['log_level'],
    format=LOGGING_CONFIG['log_format']
)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles real-time audio capture and speech emotion recognition"""
    
    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_running = False
        self.current_emotions = {}
        self.lock = threading.Lock()
        
        # Model components
        self.model = None
        self.processor = None
        self.device = None
        
        # Audio buffer
        self.audio_buffer = []
        self.buffer_duration = AUDIO_CONFIG['chunk_duration']
        self.sample_rate = AUDIO_CONFIG['sample_rate']
        
    def initialize(self) -> bool:
        """Initialize audio capture and load emotion recognition model"""
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Setup device (MPS for Apple M3)
            if OPTIMIZATION_CONFIG['use_gpu'] and torch.backends.mps.is_available():
                self.device = torch.device('mps')
                logger.info("Using MPS (Metal Performance Shaders) for audio processing")
            else:
                self.device = torch.device('cpu')
                logger.info("Using CPU for audio processing")
            
            # Load pre-trained Wav2Vec2 emotion model
            logger.info(f"Loading audio emotion model: {MODEL_CONFIG['audio_model']}")
            self.processor = Wav2Vec2Processor.from_pretrained(MODEL_CONFIG['audio_model'])
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_CONFIG['audio_model'])
            self.model.to(self.device)
            self.model.eval()
            
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=AUDIO_CONFIG['channels'],
                rate=AUDIO_CONFIG['sample_rate'],
                input=True,
                frames_per_buffer=AUDIO_CONFIG['chunk_size'],
                stream_callback=self._audio_callback
            )
            
            logger.info("Audio processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing audio processor: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_buffer.append(audio_data)
        
        return (in_data, pyaudio.paContinue)
    
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Process an audio chunk and extract emotion scores
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            Dictionary of emotion scores (0-1 range) or None if processing fails
        """
        try:
            # Ensure audio is the right length
            target_length = int(self.sample_rate * self.buffer_duration)
            
            if len(audio_chunk) < target_length:
                # Pad if too short
                audio_chunk = np.pad(audio_chunk, (0, target_length - len(audio_chunk)))
            elif len(audio_chunk) > target_length:
                # Truncate if too long
                audio_chunk = audio_chunk[:target_length]
            
            # Process audio with Wav2Vec2
            inputs = self.processor(
                audio_chunk,
                sampling_rate=self.sample_rate,
                return_tensors="pt",
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                logits = self.model(**inputs).logits
            
            # Convert to probabilities
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            probabilities = probabilities.cpu().numpy()[0]
            
            # Map to emotion labels
            emotion_labels = self.model.config.id2label
            emotions = {
                emotion_labels[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }
            
            # Map model outputs to our standard emotion names
            mapped_emotions = self._map_emotions(emotions)
            
            return mapped_emotions
            
        except Exception as e:
            logger.warning(f"Error processing audio chunk: {e}")
            return None
    
    def _map_emotions(self, raw_emotions: Dict[str, float]) -> Dict[str, float]:
        """
        Map model-specific emotion labels to standardized emotion names
        
        The Wav2Vec2 model may use different emotion labels,
        so we map them to our standard set
        """
        # Standard mapping (adjust based on actual model output)
        emotion_mapping = {
            'angry': 'angry',
            'calm': 'calm',
            'disgust': 'disgust',
            'fear': 'fear',
            'happy': 'happy',
            'neutral': 'neutral',
            'sad': 'sad',
            'surprise': 'surprise',
            # Additional mappings for extended emotions
            'excited': 'excited',
            'frustrated': 'frustrated',
        }
        
        # Create mapped emotions with default values
        mapped = {
            'calm': 0.0,
            'excited': 0.0,
            'frustrated': 0.0,
            'engaged': 0.0,
            'confused': 0.0,
            'anxious': 0.0,
            'confident': 0.0,
            'interested': 0.0,
            'bored': 0.0,
            'curious': 0.0,
            'stressed': 0.0,
        }
        
        # Map raw emotions
        for raw_label, score in raw_emotions.items():
            raw_label_lower = raw_label.lower()
            if raw_label_lower in emotion_mapping:
                std_label = emotion_mapping[raw_label_lower]
                if std_label in mapped:
                    mapped[std_label] = score
        
        # Derive additional emotions from available data
        # These are heuristic mappings
        if 'angry' in raw_emotions:
            mapped['frustrated'] = max(mapped['frustrated'], raw_emotions['angry'] * 0.7)
            mapped['stressed'] = max(mapped['stressed'], raw_emotions['angry'] * 0.5)
        
        if 'calm' in raw_emotions:
            mapped['calm'] = raw_emotions['calm']
            mapped['confident'] = raw_emotions['calm'] * 0.6
        
        if 'happy' in raw_emotions:
            mapped['excited'] = raw_emotions['happy'] * 0.7
            mapped['engaged'] = raw_emotions['happy'] * 0.5
            mapped['interested'] = raw_emotions['happy'] * 0.6
        
        if 'neutral' in raw_emotions:
            mapped['bored'] = raw_emotions['neutral'] * 0.4
        
        if 'surprise' in raw_emotions:
            mapped['curious'] = raw_emotions['surprise'] * 0.8
            mapped['interested'] = max(mapped['interested'], raw_emotions['surprise'] * 0.6)
        
        if 'fear' in raw_emotions:
            mapped['anxious'] = raw_emotions['fear'] * 0.9
            mapped['confused'] = raw_emotions['fear'] * 0.4
        
        return mapped
    
    def get_emotions(self) -> Dict[str, float]:
        """Get current emotion scores (thread-safe)"""
        with self.lock:
            return self.current_emotions.copy()
    
    def start(self):
        """Start audio processing"""
        if not self.initialize():
            logger.error("Failed to initialize audio processor")
            return
        
        self.is_running = True
        self.stream.start_stream()
        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_thread.start()
        logger.info("Audio processor started")
    
    def _process_loop(self):
        """Main processing loop (runs in separate thread)"""
        samples_per_chunk = int(self.sample_rate * self.buffer_duration)
        
        while self.is_running:
            try:
                # Check if we have enough audio data
                if len(self.audio_buffer) > 0:
                    # Concatenate buffer
                    audio_data = np.concatenate(self.audio_buffer)
                    
                    # Clear buffer
                    self.audio_buffer = []
                    
                    # Process if we have enough data
                    if len(audio_data) >= samples_per_chunk:
                        emotions = self.process_audio_chunk(audio_data)
                        
                        if emotions:
                            with self.lock:
                                self.current_emotions = emotions
                        else:
                            # Use default values if processing fails
                            with self.lock:
                                if not self.current_emotions:
                                    self.current_emotions = {
                                        'calm': 0.5,
                                        'excited': 0.0,
                                        'frustrated': 0.0,
                                        'engaged': 0.3,
                                        'confused': 0.0,
                                        'anxious': 0.0,
                                        'confident': 0.5,
                                        'interested': 0.3,
                                        'bored': 0.0,
                                        'curious': 0.0,
                                        'stressed': 0.0,
                                    }
                
                # Sleep to prevent CPU overload
                time.sleep(PROCESSING_CONFIG['update_frequency'])
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.1)
    
    def stop(self):
        """Stop audio processing and release resources"""
        logger.info("Stopping audio processor...")
        self.is_running = False
        
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=2.0)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("Audio processor stopped")


