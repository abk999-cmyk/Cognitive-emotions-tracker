/**
 * Emotion-Aware AI Chat Module
 * Handles chat interface and emotion-aware messaging
 */

// Chat state
let chatActive = false;
let currentEmotions = {};
let messageCount = 0;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const emotionIndicator = document.getElementById('emotionIndicator');

/**
 * Initialize chat module
 */
function initChat() {
    console.log('Initializing emotion-aware chat...');
    
    // Setup event listeners
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    
    // Allow Enter to send (Shift+Enter for newline)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Add welcome message
    addSystemMessage("Hello! I'm your emotion-aware AI assistant. I can sense your emotional state and adapt my responses accordingly. How can I help you today?");
    
    console.log('Chat initialized');
}

/**
 * Update current emotions for chat context
 */
function updateChatEmotions(emotions) {
    currentEmotions = emotions;
    updateEmotionIndicator(emotions);
}

/**
 * Update emotion indicator display
 */
function updateEmotionIndicator(emotions) {
    if (!emotions || Object.keys(emotions).length === 0) {
        emotionIndicator.textContent = '🧠 Analyzing your mood...';
        return;
    }
    
    // Find dominant emotion
    let maxEmotion = null;
    let maxScore = 0;
    
    Object.entries(emotions).forEach(([emotion, score]) => {
        if (score > maxScore) {
            maxScore = score;
            maxEmotion = emotion;
        }
    });
    
    // Get emoji for emotion
    const emoji = getEmotionEmoji(maxEmotion);
    
    if (maxScore > 0.3) {
        emotionIndicator.textContent = `${emoji} Sensing: ${maxEmotion} (${(maxScore * 100).toFixed(0)}%)`;
    } else {
        emotionIndicator.textContent = '🧠 Neutral emotional state';
    }
}

/**
 * Get emoji for emotion
 */
function getEmotionEmoji(emotion) {
    const emojiMap = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'fear': '😨',
        'surprise': '😲',
        'disgust': '🤢',
        'neutral': '😐',
        'calm': '😌',
        'excited': '🤩',
        'frustrated': '😤',
        'engaged': '🤔',
        'confused': '😕',
        'anxious': '😰',
        'confident': '😎',
        'interested': '🧐',
        'bored': '😑',
        'curious': '🤨',
        'stressed': '😫',
        'receptiveness': '👂',
        'awareness': '👁️',
        'trust': '🤝',
        'anticipation': '⏰',
        'relaxed': '😊',
        'skeptical': '🤨',
        'distracted': '😵',
        'enthusiastic': '🎉',
        'contemplative': '🤔',
        'alert': '⚡'
    };
    
    return emojiMap[emotion] || '🧠';
}

/**
 * Send a message to the AI
 */
async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input while sending
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        // Send to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                emotions: currentEmotions
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.success) {
            // Add AI response
            addAIMessage(data.response, data.tone_used, data.emotions_detected);
            messageCount++;
        } else {
            // Show error
            addErrorMessage(data.error || 'Failed to get response');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addErrorMessage('Connection error. Please try again.');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

/**
 * Add user message to chat
 */
function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user-bubble';
    bubble.textContent = message;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(bubble);
    messageDiv.appendChild(timestamp);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add AI message to chat
 */
function addAIMessage(message, tone, emotions) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message ai-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble ai-bubble';
    bubble.textContent = message;
    
    const metadata = document.createElement('div');
    metadata.className = 'message-metadata';
    
    if (tone) {
        const toneSpan = document.createElement('span');
        toneSpan.className = 'message-tone';
        toneSpan.textContent = `Tone: ${tone}`;
        metadata.appendChild(toneSpan);
    }
    
    if (emotions && emotions.length > 0) {
        const emotionsSpan = document.createElement('span');
        emotionsSpan.className = 'message-emotions';
        emotionsSpan.textContent = `Detected: ${emotions.join(', ')}`;
        metadata.appendChild(emotionsSpan);
    }
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(bubble);
    if (metadata.children.length > 0) {
        messageDiv.appendChild(metadata);
    }
    messageDiv.appendChild(timestamp);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add system message
 */
function addSystemMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message system-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble system-bubble';
    bubble.textContent = message;
    
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add error message
 */
function addErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message error-message';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble error-bubble';
    bubble.textContent = `⚠️ ${message}`;
    
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

/**
 * Add typing indicator
 */
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai-message typing-indicator';
    typingDiv.id = `typing-${Date.now()}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble ai-bubble typing-bubble';
    bubble.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    
    typingDiv.appendChild(bubble);
    chatMessages.appendChild(typingDiv);
    
    scrollToBottom();
    
    return typingDiv.id;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(id) {
    const typingDiv = document.getElementById(id);
    if (typingDiv) {
        typingDiv.remove();
    }
}

/**
 * Clear chat history
 */
async function clearChat() {
    if (!confirm('Are you sure you want to clear the conversation history?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/chat/reset', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear messages
            chatMessages.innerHTML = '';
            messageCount = 0;
            
            // Add welcome message back
            addSystemMessage("Conversation cleared. How can I help you?");
            
            showChatNotification('Chat history cleared', 'success');
        } else {
            showChatNotification('Failed to clear history', 'error');
        }
    } catch (error) {
        console.error('Error clearing chat:', error);
        showChatNotification('Connection error', 'error');
    }
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Show chat notification
 */
function showChatNotification(message, type) {
    // Use the same notification system from dashboard.js if available
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        console.log(`[${type}] ${message}`);
    }
}

// Export functions for use in dashboard
window.chatModule = {
    initChat,
    updateChatEmotions,
    sendMessage,
    clearChat
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChat);
} else {
    initChat();
}

