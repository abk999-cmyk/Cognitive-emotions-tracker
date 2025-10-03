"""
Emotion Fusion Module
Combines video and audio emotion scores into a comprehensive emotion profile
"""

import numpy as np
import logging
from typing import Dict
from config import EMOTION_LIST, FUSION_WEIGHTS, PROCESSING_CONFIG, LOGGING_CONFIG

# Setup logging
logging.basicConfig(
    filename=LOGGING_CONFIG['log_file'],
    level=LOGGING_CONFIG['log_level'],
    format=LOGGING_CONFIG['log_format']
)
logger = logging.getLogger(__name__)


class EmotionFusion:
    """Fuses multimodal emotion data from video and audio"""
    
    def __init__(self):
        self.previous_scores = {}
        self.smoothing_alpha = PROCESSING_CONFIG['temporal_smoothing_alpha']
        self.video_weight = FUSION_WEIGHTS['video']
        self.audio_weight = FUSION_WEIGHTS['audio']
        
        # Initialize with zeros
        self.previous_scores = {emotion: 0.0 for emotion in EMOTION_LIST}
    
    def fuse_emotions(
        self,
        video_emotions: Dict[str, float],
        audio_emotions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Combine video and audio emotion scores into unified emotion profile
        
        Args:
            video_emotions: Emotion scores from facial analysis
            audio_emotions: Emotion scores from speech analysis
            
        Returns:
            Dictionary with all 25-30 emotions normalized to 0-1 range
        """
        fused_emotions = {}
        
        # Process base visual emotions
        for emotion in ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']:
            video_score = video_emotions.get(emotion, 0.0)
            fused_emotions[emotion] = video_score * self.video_weight
        
        # Process base audio emotions
        for emotion in ['calm', 'excited', 'frustrated', 'engaged', 'confused', 
                       'anxious', 'confident', 'interested', 'bored', 'curious', 'stressed']:
            audio_score = audio_emotions.get(emotion, 0.0)
            fused_emotions[emotion] = audio_score * self.audio_weight
        
        # Derive composite emotions
        fused_emotions.update(self._derive_composite_emotions(video_emotions, audio_emotions))
        
        # Apply temporal smoothing
        fused_emotions = self._apply_temporal_smoothing(fused_emotions)
        
        # Normalize to 0-1 range
        fused_emotions = self._normalize_scores(fused_emotions)
        
        # Update previous scores
        self.previous_scores = fused_emotions.copy()
        
        return fused_emotions
    
    def _derive_composite_emotions(
        self,
        video_emotions: Dict[str, float],
        audio_emotions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Derive complex emotions from combinations of base emotions
        """
        composite = {}
        
        # Receptiveness: engagement + positive emotions
        engaged = audio_emotions.get('engaged', 0.0)
        happy = video_emotions.get('happy', 0.0)
        interested = audio_emotions.get('interested', 0.0)
        composite['receptiveness'] = (engaged * 0.5 + happy * 0.3 + interested * 0.2)
        
        # Awareness: attention indicators
        surprise = video_emotions.get('surprise', 0.0)
        interested = audio_emotions.get('interested', 0.0)
        engaged = audio_emotions.get('engaged', 0.0)
        composite['awareness'] = (surprise * 0.3 + interested * 0.4 + engaged * 0.3)
        
        # Trust: calm + happy
        calm = audio_emotions.get('calm', 0.0)
        happy = video_emotions.get('happy', 0.0)
        confident = audio_emotions.get('confident', 0.0)
        composite['trust'] = (calm * 0.4 + happy * 0.3 + confident * 0.3)
        
        # Anticipation: excited + curious
        excited = audio_emotions.get('excited', 0.0)
        curious = audio_emotions.get('curious', 0.0)
        surprise = video_emotions.get('surprise', 0.0)
        composite['anticipation'] = (excited * 0.4 + curious * 0.4 + surprise * 0.2)
        
        # Relaxed: calm + neutral
        calm = audio_emotions.get('calm', 0.0)
        neutral = video_emotions.get('neutral', 0.0)
        composite['relaxed'] = (calm * 0.6 + neutral * 0.4)
        
        # Skeptical: confused + neutral
        confused = audio_emotions.get('confused', 0.0)
        neutral = video_emotions.get('neutral', 0.0)
        composite['skeptical'] = (confused * 0.6 + neutral * 0.4)
        
        # Distracted: inverse of engaged
        engaged = audio_emotions.get('engaged', 0.0)
        bored = audio_emotions.get('bored', 0.0)
        composite['distracted'] = (1.0 - engaged) * 0.5 + bored * 0.5
        
        # Enthusiastic: excited + happy
        excited = audio_emotions.get('excited', 0.0)
        happy = video_emotions.get('happy', 0.0)
        composite['enthusiastic'] = (excited * 0.6 + happy * 0.4)
        
        # Contemplative: neutral + interested
        neutral = video_emotions.get('neutral', 0.0)
        interested = audio_emotions.get('interested', 0.0)
        composite['contemplative'] = (neutral * 0.5 + interested * 0.5)
        
        # Alert: awareness + surprise
        surprise = video_emotions.get('surprise', 0.0)
        engaged = audio_emotions.get('engaged', 0.0)
        composite['alert'] = (surprise * 0.6 + engaged * 0.4)
        
        return composite
    
    def _apply_temporal_smoothing(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Apply exponential moving average to smooth emotion transitions
        Prevents jittery updates
        
        smoothed = alpha * current + (1 - alpha) * previous
        """
        smoothed = {}
        
        for emotion in EMOTION_LIST:
            current = current_scores.get(emotion, 0.0)
            previous = self.previous_scores.get(emotion, 0.0)
            
            # Exponential moving average
            smoothed[emotion] = (
                self.smoothing_alpha * current + 
                (1 - self.smoothing_alpha) * previous
            )
        
        return smoothed
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Ensure all scores are in valid 0-1 range
        """
        normalized = {}
        
        for emotion, score in scores.items():
            # Clip to 0-1 range
            normalized[emotion] = np.clip(score, 0.0, 1.0)
        
        return normalized
    
    def get_all_emotions(
        self,
        video_emotions: Dict[str, float],
        audio_emotions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Main method to get complete emotion profile
        
        Returns all 25-30 emotions with scores 0-1
        """
        try:
            fused = self.fuse_emotions(video_emotions, audio_emotions)
            
            # Ensure all emotions from EMOTION_LIST are present
            complete_emotions = {}
            for emotion in EMOTION_LIST:
                complete_emotions[emotion] = fused.get(emotion, 0.0)
            
            return complete_emotions
            
        except Exception as e:
            logger.error(f"Error in emotion fusion: {e}")
            # Return safe default values
            return {emotion: 0.0 for emotion in EMOTION_LIST}
    
    def reset(self):
        """Reset temporal smoothing state"""
        self.previous_scores = {emotion: 0.0 for emotion in EMOTION_LIST}
        logger.info("Emotion fusion state reset")


