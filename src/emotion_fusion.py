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
        Works with video-only if audio fails
        
        Args:
            video_emotions: Emotion scores from facial analysis
            audio_emotions: Emotion scores from speech analysis
            
        Returns:
            Dictionary with all 25-30 emotions normalized to 0-1 range
        """
        fused_emotions = {}
        sensitivity_boost = PROCESSING_CONFIG.get('sensitivity_boost', 1.0)
        
        # Check if audio is working
        audio_working = any(audio_emotions.values()) if audio_emotions else False
        
        # Process base visual emotions with sensitivity boost
        for emotion in ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']:
            video_score = video_emotions.get(emotion, 0.0)
            # Apply sensitivity boost to amplify small changes
            boosted_score = min(1.0, video_score * sensitivity_boost)
            fused_emotions[emotion] = boosted_score
        
        # If audio isn't working, derive audio emotions from video
        if not audio_working:
            # Derive audio-like emotions from facial expressions (reduced multipliers to prevent maxing)
            fused_emotions['calm'] = min(0.85, (video_emotions.get('neutral', 0.0) * 0.5 + 
                                               (1.0 - video_emotions.get('angry', 0.0)) * 0.2) * sensitivity_boost)
            fused_emotions['excited'] = min(0.85, (video_emotions.get('happy', 0.0) * 0.6 + 
                                                   video_emotions.get('surprise', 0.0) * 0.3) * sensitivity_boost)
            fused_emotions['frustrated'] = min(0.85, (video_emotions.get('angry', 0.0) * 0.6 + 
                                                      video_emotions.get('disgust', 0.0) * 0.2) * sensitivity_boost)
            fused_emotions['engaged'] = min(0.85, (1.0 - video_emotions.get('neutral', 0.0)) * 0.4 * sensitivity_boost)
            fused_emotions['confused'] = min(0.85, (video_emotions.get('surprise', 0.0) * 0.3 + 
                                                    video_emotions.get('fear', 0.0) * 0.2) * sensitivity_boost)
            fused_emotions['anxious'] = min(0.85, (video_emotions.get('fear', 0.0) * 0.7 + 
                                                   video_emotions.get('sad', 0.0) * 0.2) * sensitivity_boost)
            fused_emotions['confident'] = min(0.85, (video_emotions.get('happy', 0.0) * 0.4 + 
                                                     (1.0 - video_emotions.get('fear', 0.0)) * 0.2) * sensitivity_boost)
            fused_emotions['interested'] = min(0.85, (video_emotions.get('surprise', 0.0) * 0.4 + 
                                                      video_emotions.get('happy', 0.0) * 0.3) * sensitivity_boost)
            fused_emotions['bored'] = min(0.85, video_emotions.get('neutral', 0.0) * 0.4 * sensitivity_boost)
            fused_emotions['curious'] = min(0.85, (video_emotions.get('surprise', 0.0) * 0.6 + 
                                                   (1.0 - video_emotions.get('neutral', 0.0)) * 0.15) * sensitivity_boost)
            fused_emotions['stressed'] = min(0.85, (video_emotions.get('angry', 0.0) * 0.4 + 
                                                    video_emotions.get('fear', 0.0) * 0.4) * sensitivity_boost)
        else:
            # Process audio emotions normally
            for emotion in ['calm', 'excited', 'frustrated', 'engaged', 'confused', 
                           'anxious', 'confident', 'interested', 'bored', 'curious', 'stressed']:
                audio_score = audio_emotions.get(emotion, 0.0)
                boosted_score = min(1.0, audio_score * sensitivity_boost)
                fused_emotions[emotion] = boosted_score * self.audio_weight
        
        # Derive composite emotions
        fused_emotions.update(self._derive_composite_emotions(video_emotions, fused_emotions if not audio_working else audio_emotions))
        
        # Apply temporal smoothing
        fused_emotions = self._apply_temporal_smoothing(fused_emotions)
        
        # Add micro-variation to prevent stuck values (smaller to avoid spikes)
        import random
        for emotion in fused_emotions:
            if fused_emotions[emotion] > 0.05:  # Only vary emotions that are active
                variation = random.uniform(-0.01, 0.01)  # Smaller variation
                fused_emotions[emotion] = max(0.0, min(0.95, fused_emotions[emotion] + variation))  # Cap at 0.95
        
        # Normalize to 0-1 range but cap maximum
        fused_emotions = self._normalize_scores(fused_emotions)
        # Ensure no emotion maxes out completely
        for emotion in fused_emotions:
            if fused_emotions[emotion] > 0.92:
                fused_emotions[emotion] = 0.92
        
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
        More sensitive to small changes
        """
        composite = {}
        boost = PROCESSING_CONFIG.get('sensitivity_boost', 1.0)
        
        # Receptiveness: engagement + positive emotions (balanced)
        engaged = audio_emotions.get('engaged', 0.0) * boost
        happy = video_emotions.get('happy', 0.0) * boost
        interested = audio_emotions.get('interested', 0.0) * boost
        composite['receptiveness'] = min(0.88, engaged * 0.3 + happy * 0.25 + interested * 0.2)
        
        # Awareness: attention indicators (balanced)
        surprise = video_emotions.get('surprise', 0.0) * boost
        interested = audio_emotions.get('interested', 0.0) * boost
        engaged = audio_emotions.get('engaged', 0.0) * boost
        composite['awareness'] = min(0.88, surprise * 0.25 + interested * 0.25 + engaged * 0.25)
        
        # Trust: calm + happy + confident (balanced)
        calm = audio_emotions.get('calm', 0.0) * boost
        happy = video_emotions.get('happy', 0.0) * boost
        confident = audio_emotions.get('confident', 0.0) * boost
        composite['trust'] = min(0.88, calm * 0.25 + happy * 0.2 + confident * 0.25)
        
        # Anticipation: excited + curious (balanced)
        excited = audio_emotions.get('excited', 0.0) * boost
        curious = audio_emotions.get('curious', 0.0) * boost
        surprise = video_emotions.get('surprise', 0.0) * boost
        composite['anticipation'] = min(0.88, excited * 0.3 + curious * 0.25 + surprise * 0.2)
        
        # Relaxed: calm + neutral (balanced)
        calm = audio_emotions.get('calm', 0.0) * boost
        neutral = video_emotions.get('neutral', 0.0) * boost
        composite['relaxed'] = min(0.88, calm * 0.35 + neutral * 0.3)
        
        # Skeptical: confused + neutral (balanced)
        confused = audio_emotions.get('confused', 0.0) * boost
        neutral = video_emotions.get('neutral', 0.0)
        composite['skeptical'] = min(0.88, confused * 0.4 + neutral * 0.2)
        
        # Distracted: inverse of engaged (balanced)
        engaged = audio_emotions.get('engaged', 0.0)
        bored = audio_emotions.get('bored', 0.0) * boost
        neutral = video_emotions.get('neutral', 0.0)
        composite['distracted'] = min(0.88, (1.0 - engaged) * 0.25 + bored * 0.25 + neutral * 0.15)
        
        # Enthusiastic: excited + happy (balanced)
        excited = audio_emotions.get('excited', 0.0) * boost
        happy = video_emotions.get('happy', 0.0) * boost
        composite['enthusiastic'] = min(0.88, excited * 0.4 + happy * 0.3)
        
        # Contemplative: neutral + interested (balanced)
        neutral = video_emotions.get('neutral', 0.0)
        interested = audio_emotions.get('interested', 0.0) * boost
        composite['contemplative'] = min(0.88, neutral * 0.25 + interested * 0.4)
        
        # Alert: awareness + surprise (balanced)
        surprise = video_emotions.get('surprise', 0.0) * boost
        engaged = audio_emotions.get('engaged', 0.0) * boost
        composite['alert'] = min(0.88, surprise * 0.4 + engaged * 0.3)
        
        return composite
    
    def _apply_temporal_smoothing(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Apply exponential moving average to smooth emotion transitions
        Prevents jittery updates and allows emotions to persist
        
        smoothed = alpha * current + (1 - alpha) * previous
        """
        smoothed = {}
        decay_rate = PROCESSING_CONFIG.get('emotion_decay_rate', 0.9)
        
        for emotion in EMOTION_LIST:
            current = current_scores.get(emotion, 0.0)
            previous = self.previous_scores.get(emotion, 0.0)
            
            # If current value is higher, update quickly
            # If current is lower, decay gradually
            if current >= previous:
                # Rise quickly to new emotions
                smoothed[emotion] = (
                    self.smoothing_alpha * current + 
                    (1 - self.smoothing_alpha) * previous
                )
            else:
                # Decay slowly when emotion reduces
                smoothed[emotion] = max(
                    current,
                    previous * decay_rate  # Gradual decay instead of instant drop
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


