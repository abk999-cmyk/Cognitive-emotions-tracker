"""
OpenAI Chat Module with Emotion-Aware Prompting
Integrates real-time emotion tracking into AI assistant responses
"""

import os
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from openai import OpenAI

from config import OPENAI_CONFIG, EMOTION_LIST

logger = logging.getLogger(__name__)


class EmotionAwareChatbot:
    """
    OpenAI-powered chatbot that adapts responses based on user's emotional state
    """
    
    def __init__(self):
        """Initialize the emotion-aware chatbot"""
        self.client = OpenAI(api_key=OPENAI_CONFIG['api_key'])
        self.model = OPENAI_CONFIG['model']
        self.max_tokens = OPENAI_CONFIG['max_tokens']
        self.temperature = OPENAI_CONFIG['temperature']
        
        # Conversation history
        self.conversation_history: List[Dict] = []
        self.max_history = OPENAI_CONFIG.get('max_history', 10)
        
        # Rate limiting
        self.message_timestamps: List[float] = []
        self.rate_limit = OPENAI_CONFIG.get('rate_limit', 30)
        
        logger.info("Emotion-aware chatbot initialized")
    
    def build_emotion_context(self, emotions: Dict[str, float]) -> Tuple[str, List[str], str]:
        """
        Build emotion context for the system prompt
        
        Args:
            emotions: Dictionary of emotion scores (0.0-1.0)
            
        Returns:
            Tuple of (emotion_profile_text, high_emotions_list, dominant_emotion)
        """
        # Format all emotions
        emotion_lines = []
        for emotion in EMOTION_LIST:
            score = emotions.get(emotion, 0.0)
            emotion_lines.append(f"- {emotion.capitalize()}: {score:.2f}")
        
        emotion_profile = "\n".join(emotion_lines)
        
        # Identify high emotions (>0.6)
        high_emotions = [
            emotion for emotion, score in emotions.items() 
            if score > 0.6
        ]
        
        # Find dominant emotion
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            dominant_name = dominant_emotion[0]
            dominant_score = dominant_emotion[1]
        else:
            dominant_name = "neutral"
            dominant_score = 0.0
        
        return emotion_profile, high_emotions, f"{dominant_name} ({dominant_score:.2f})"
    
    def build_system_prompt(self, emotions: Dict[str, float]) -> str:
        """
        Build the emotion-aware system prompt
        
        Args:
            emotions: Current emotion scores
            
        Returns:
            Complete system prompt with emotion context
        """
        emotion_profile, high_emotions, dominant_emotion = self.build_emotion_context(emotions)
        
        high_emotions_str = ", ".join(high_emotions) if high_emotions else "None"
        
        system_prompt = f"""You are an empathetic AI assistant with emotional intelligence. 
You are currently talking to someone with the following emotional state:

EMOTIONAL PROFILE (scale 0.0-1.0):
{emotion_profile}

HIGH EMOTIONS (>0.6): {high_emotions_str}
DOMINANT EMOTION: {dominant_emotion}

RESPONSE GUIDELINES:
- If anxious/stressed (>0.5): Be calming, reassuring, break things into simple steps
- If sad/depressed (>0.5): Show empathy, validate feelings, offer support
- If happy/excited (>0.6): Match enthusiasm, be celebratory, use positive energy
- If angry/frustrated (>0.5): Stay calm, acknowledge frustration, offer solutions
- If confused (>0.5): Be clear, patient, explain step-by-step
- If bored (>0.5): Be engaging, interesting, ask questions
- If engaged/interested (>0.6): Dive deeper, provide detailed information
- If neutral: Be balanced and professional

ADDITIONAL GUIDELINES:
- Adapt your tone, word choice, and response length based on their emotional state
- Be authentic and genuinely helpful
- If multiple strong emotions are present, acknowledge the complexity
- Show awareness of their emotional state naturally, without being overly explicit
- Provide practical support when appropriate
- Be concise but warm (aim for 2-4 sentences unless more detail is needed)

Remember: The user may not be explicitly aware of their emotional state. Your job is to respond in a way that naturally aligns with and supports their current emotional needs."""
        
        return system_prompt
    
    def check_rate_limit(self) -> bool:
        """
        Check if rate limit has been exceeded
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        
        # Remove timestamps older than 1 minute
        self.message_timestamps = [
            ts for ts in self.message_timestamps 
            if now - ts < 60
        ]
        
        # Check if under limit
        if len(self.message_timestamps) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded: {len(self.message_timestamps)} messages in last minute")
            return False
        
        # Add current timestamp
        self.message_timestamps.append(now)
        return True
    
    def send_message(
        self, 
        user_message: str, 
        emotions: Dict[str, float]
    ) -> Dict:
        """
        Send a message to the AI with emotion context
        
        Args:
            user_message: User's message
            emotions: Current emotion scores
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Check rate limit
            if not self.check_rate_limit():
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait a moment.',
                    'response': None
                }
            
            # Build system prompt with emotion context
            system_prompt = self.build_system_prompt(emotions)
            
            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history (last N messages)
            recent_history = self.conversation_history[-self.max_history:]
            messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            logger.info(f"Sending message to OpenAI with {len(emotions)} emotion scores")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Identify which emotions influenced the response
            _, high_emotions, dominant_emotion = self.build_emotion_context(emotions)
            
            # Determine tone used
            tone = self._determine_tone(emotions)
            
            logger.info(f"Generated response with tone: {tone}")
            
            return {
                'success': True,
                'response': ai_response,
                'emotions_detected': high_emotions,
                'dominant_emotion': dominant_emotion,
                'tone_used': tone,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error sending message to OpenAI: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "I apologize, but I'm having trouble connecting right now. Please try again in a moment."
            }
    
    def _determine_tone(self, emotions: Dict[str, float]) -> str:
        """
        Determine the tone that should be used based on emotions
        
        Args:
            emotions: Current emotion scores
            
        Returns:
            Description of tone
        """
        anxious = emotions.get('anxious', 0.0)
        stressed = emotions.get('stressed', 0.0)
        sad = emotions.get('sad', 0.0)
        happy = emotions.get('happy', 0.0)
        excited = emotions.get('excited', 0.0)
        angry = emotions.get('angry', 0.0)
        frustrated = emotions.get('frustrated', 0.0)
        confused = emotions.get('confused', 0.0)
        bored = emotions.get('bored', 0.0)
        engaged = emotions.get('engaged', 0.0)
        
        # Determine primary tone
        if anxious > 0.5 or stressed > 0.5:
            return "calming, reassuring"
        elif sad > 0.5:
            return "empathetic, supportive"
        elif happy > 0.6 or excited > 0.6:
            return "enthusiastic, celebratory"
        elif angry > 0.5 or frustrated > 0.5:
            return "calm, solution-focused"
        elif confused > 0.5:
            return "clear, patient"
        elif bored > 0.5:
            return "engaging, stimulating"
        elif engaged > 0.6:
            return "detailed, informative"
        else:
            return "balanced, professional"
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get the current conversation history
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_stats(self) -> Dict:
        """
        Get chatbot statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'messages_in_history': len(self.conversation_history),
            'messages_last_minute': len(self.message_timestamps),
            'rate_limit': self.rate_limit,
            'model': self.model
        }

