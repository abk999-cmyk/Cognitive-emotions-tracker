# Emotion-Aware AI Chat System Documentation

## Overview

The AI Emotion Tracking System now includes an **Emotion-Aware AI Chat Assistant** powered by OpenAI's GPT-4o. This assistant adapts its responses in real-time based on the user's emotional state detected through video and audio analysis.

## Key Features

### 🧠 Emotional Intelligence
- **Real-Time Emotion Detection**: Analyzes 28+ emotions from facial expressions and voice
- **Adaptive Responses**: Adjusts tone, empathy level, and communication style
- **Context Awareness**: Maintains conversation history while tracking mood changes
- **Intelligent Prompting**: Custom system prompts built dynamically based on emotional state

### 💬 Chat Capabilities
- **Natural Conversation**: GPT-4o powered responses
- **Emotion Context**: Every message includes full emotional profile
- **Tone Adaptation**: Responses calibrated for:
  - Anxious/Stressed → Calming, reassuring
  - Sad → Empathetic, supportive
  - Happy/Excited → Enthusiastic, celebratory
  - Angry/Frustrated → Calm, solution-focused
  - Confused → Clear, patient explanations
  - Bored → Engaging, stimulating
  - Engaged → Detailed, informative

### 🎨 User Interface
- **Modern Chat Design**: Beautiful gradient message bubbles
- **Emotion Indicator**: Live display of detected emotional state
- **Message Metadata**: Shows tone and detected emotions for each response
- **Typing Indicators**: Smooth UX with animated typing dots
- **Conversation Management**: Clear history, scroll to bottom

## Architecture

### System Flow
```
User Message → Capture Current Emotions (28 emotions) → Build Enhanced Prompt → 
OpenAI GPT-4o API → Emotion-Aware Response → Display in Chat UI
```

### Backend Components

#### 1. `src/openai_chat.py` - EmotionAwareChatbot Class
**Key Methods:**
- `build_emotion_context()` - Formats emotion data for prompts
- `build_system_prompt()` - Creates dynamic system prompts with emotion guidelines
- `send_message()` - Sends messages with emotion context to OpenAI
- `check_rate_limit()` - Prevents API abuse (30 msgs/min)
- `_determine_tone()` - Analyzes emotions to select appropriate tone

**Features:**
- Conversation history (last 10 messages)
- Rate limiting (30 messages per minute)
- Error handling and retry logic
- Emotion-based tone detection

#### 2. `src/config.py` - OpenAI Configuration
```python
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'model': 'gpt-4o',
    'max_tokens': 500,
    'temperature': 0.8,
    'rate_limit': 30,
    'max_history': 10
}
```

#### 3. `src/app.py` - API Routes
- **POST `/api/chat`** - Send message with emotion context
- **GET `/api/chat/history`** - Retrieve conversation history
- **DELETE `/api/chat/reset`** - Clear conversation
- **GET `/api/chat/stats`** - Get chatbot statistics

### Frontend Components

#### 1. `static/js/chat.js` - Chat Interface Logic
**Functions:**
- `sendMessage()` - Sends messages to backend with emotions
- `updateChatEmotions()` - Updates emotion context in real-time
- `updateEmotionIndicator()` - Displays current emotional state
- `addUserMessage()` / `addAIMessage()` - Renders chat bubbles
- `addTypingIndicator()` - Shows loading state
- `clearChat()` - Resets conversation

#### 2. `templates/index.html` - Chat UI
- Chat section with header
- Scrollable messages container
- Textarea input with Send/Clear buttons
- Emotion indicator badge

#### 3. `static/css/style.css` - Chat Styling
- Modern gradient message bubbles
- User messages: Blue gradient, right-aligned
- AI messages: Pink gradient, left-aligned
- System messages: Gray, centered
- Smooth animations and transitions

## Emotion-Aware Prompting Strategy

### System Prompt Template
```
You are an empathetic AI assistant with emotional intelligence. 
You are currently talking to someone with the following emotional state:

EMOTIONAL PROFILE (scale 0.0-1.0):
- Happy: 0.45
- Sad: 0.12
- Anxious: 0.67
... [all 28 emotions]

HIGH EMOTIONS (>0.6): anxious, stressed
DOMINANT EMOTION: anxious (0.67)

RESPONSE GUIDELINES:
[Dynamic guidelines based on emotional state]
```

### Tone Determination Logic
| Emotion Score | Tone Applied |
|--------------|--------------|
| Anxious/Stressed > 0.5 | Calming, reassuring, break into steps |
| Sad > 0.5 | Empathetic, supportive, validate feelings |
| Happy/Excited > 0.6 | Match enthusiasm, celebratory |
| Angry/Frustrated > 0.5 | Stay calm, acknowledge, offer solutions |
| Confused > 0.5 | Clear, patient, step-by-step |
| Bored > 0.5 | Engaging, interesting, ask questions |
| Engaged > 0.6 | Detailed, dive deeper |
| Neutral | Balanced, professional |

## Example Interactions

### Scenario 1: User is Anxious
**Emotions:** anxious=0.82, stressed=0.67, confused=0.45

**User:** "I don't know how to start this project"

**AI Response (Calm, Step-by-Step):**
"I can sense you're feeling a bit overwhelmed right now, and that's completely okay. Let's break this down together into small, manageable steps. First, what's one small thing about the project that you DO understand? We'll start there."

### Scenario 2: User is Happy
**Emotions:** happy=0.89, excited=0.76, confident=0.68

**User:** "I just got promoted!"

**AI Response (Enthusiastic, Celebratory):**
"That's AMAZING! Congratulations! 🎉 You must be so proud - this is such a huge accomplishment! Tell me more about your new role!"

### Scenario 3: User is Sad
**Emotions:** sad=0.71, stressed=0.54, bored=0.33

**User:** "Everything feels pointless today"

**AI Response (Empathetic, Gentle):**
"I hear you, and I can tell you're going through a tough moment right now. Those feelings are valid. Sometimes days just feel heavy. Would you like to talk about what's on your mind, or would you prefer some suggestions for small things that might help lift your spirits a bit?"

## Configuration

### API Key Setup
1. API key stored in `.env` file (gitignored)
2. Loaded via `python-dotenv` in `config.py`
3. Never exposed to frontend or logs

**`.env` file:**
```bash
OPENAI_API_KEY=sk-proj-...
```

### Rate Limiting
- **Default:** 30 messages per minute
- **Purpose:** Prevent API abuse and cost control
- **Implementation:** Timestamp tracking with rolling window

### Conversation History
- **Default:** Last 10 messages
- **Purpose:** Maintain context without excessive tokens
- **Management:** Automatic pruning, manual clear option

## Security & Privacy

### API Key Protection
✅ Stored in `.env` file (gitignored)  
✅ Loaded server-side only  
✅ Never sent to frontend  
✅ Never logged  

### Rate Limiting
✅ 30 messages per minute  
✅ Per-session tracking  
✅ Error messages on limit exceeded  

### Data Privacy
✅ Conversations not logged to disk  
✅ Emotion data stays local  
✅ Clear history option available  
✅ No persistent storage  

## Technical Details

### Dependencies
```
openai==1.12.0          # OpenAI API client
python-dotenv==1.0.0    # Environment variable loading
```

### API Endpoints

#### Send Message
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "emotions": {
    "happy": 0.45,
    "sad": 0.12,
    ...
  }
}

Response:
{
  "success": true,
  "response": "Hello! I notice you're feeling...",
  "emotions_detected": ["happy"],
  "dominant_emotion": "happy (0.45)",
  "tone_used": "balanced, professional",
  "timestamp": 1696329600
}
```

#### Get History
```bash
GET /api/chat/history

Response:
{
  "success": true,
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ],
  "count": 2
}
```

#### Clear History
```bash
DELETE /api/chat/reset

Response:
{
  "success": true,
  "message": "Conversation history cleared"
}
```

### Integration with Emotion Tracking

1. **Real-Time Updates**: Dashboard.js updates chat emotions every 0.1 seconds
2. **Emotion Capture**: Chat.js captures current emotions on message send
3. **Dynamic Prompting**: OpenAI receives updated emotional state with each message
4. **Adaptive Responses**: AI adjusts based on most recent emotional readings

## Performance Considerations

### Optimization
- **M3 Chip Optimized**: Uses Apple MPS for emotion processing
- **Efficient API Calls**: Rate limited, token-optimized prompts
- **Async Operations**: Non-blocking chat requests
- **Smart Caching**: Conversation history in memory

### Response Times
- **Emotion Detection**: ~0.1 seconds (real-time)
- **OpenAI API Call**: 1-3 seconds (typical)
- **Total Response Time**: < 3 seconds
- **UI Update**: Instant with typing indicators

## Troubleshooting

### Common Issues

**Issue:** "Rate limit exceeded"  
**Solution:** Wait 60 seconds, then try again. Rate limit is 30 messages per minute.

**Issue:** "API key not found"  
**Solution:** Ensure `.env` file exists with `OPENAI_API_KEY=your-key-here`

**Issue:** "Chat not responding"  
**Solution:** Check server logs, verify OpenAI API key is valid, ensure internet connection

**Issue:** "Emotions showing as 0"  
**Solution:** Start tracking first (click "Start Tracking" button), allow camera/mic access

## Future Enhancements

### Planned Features
- 🎤 Voice chat integration
- 📊 Emotion trend analysis in conversation
- 🧘 Personalized emotion coaching
- 🌍 Multi-language support
- 💾 Conversation export
- 📈 Emotion-based conversation insights
- 🔔 Emotion change alerts ("I notice you seem more stressed now...")
- 🎯 Proactive suggestions based on emotions

## Usage Tips

1. **Start Tracking First**: Begin emotion tracking before chatting for best results
2. **Natural Conversation**: Talk normally - the AI adapts automatically
3. **Allow Camera/Mic**: Required for accurate emotion detection
4. **Clear When Needed**: Use "Clear" button to reset conversation context
5. **Observe Emotion Indicator**: Watch real-time emotion changes
6. **Check Metadata**: See which emotions influenced each response

## Credits

- **Emotion Tracking**: DeepFace, Wav2Vec2, MediaPipe
- **AI Chat**: OpenAI GPT-4o
- **Framework**: Flask, SocketIO, Python 3.11
- **Optimization**: Apple M3 MPS acceleration

---

**Version:** 1.0.0  
**Last Updated:** October 3, 2025  
**Status:** ✅ Fully Operational

