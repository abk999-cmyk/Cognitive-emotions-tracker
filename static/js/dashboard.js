/**
 * AI Emotion Tracking System - Dashboard JavaScript
 * Handles WebSocket communication and real-time UI updates
 */

// State management
let socket = null;
let isTracking = false;
let emotionData = {};

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusDot = statusIndicator.querySelector('.status-dot');
const statusText = statusIndicator.querySelector('.status-text');
const timestamp = document.getElementById('timestamp');
const emotionTableBody = document.getElementById('emotionTableBody');
const wsStatus = document.getElementById('wsStatus');
const emotionCount = document.getElementById('emotionCount');
const videoFeed = document.getElementById('videoFeed');
const videoPlaceholder = document.getElementById('videoPlaceholder');
const meshToggle = document.getElementById('meshToggle');

// Emotion list (should match backend)
const EMOTIONS = [
    'happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral',
    'calm', 'excited', 'frustrated', 'engaged', 'confused', 'anxious',
    'confident', 'interested', 'bored', 'curious', 'stressed',
    'receptiveness', 'awareness', 'trust', 'anticipation', 'relaxed',
    'skeptical', 'distracted', 'enthusiastic', 'contemplative', 'alert'
];

/**
 * Initialize the application
 */
function init() {
    console.log('Initializing AI Emotion Tracking System...');
    
    // Initialize emotion table
    initEmotionTable();
    
    // Setup WebSocket connection
    setupWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('Initialization complete');
}

/**
 * Initialize the emotion table with all emotions
 */
function initEmotionTable() {
    emotionTableBody.innerHTML = '';
    emotionCount.textContent = EMOTIONS.length;
    
    EMOTIONS.forEach(emotion => {
        const row = createEmotionRow(emotion, 0.0);
        emotionTableBody.appendChild(row);
        emotionData[emotion] = 0.0;
    });
}

/**
 * Create a table row for an emotion
 */
function createEmotionRow(emotion, score) {
    const row = document.createElement('tr');
    row.id = `emotion-${emotion}`;
    
    const nameCell = document.createElement('td');
    nameCell.className = 'emotion-name';
    nameCell.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    
    const scoreCell = document.createElement('td');
    scoreCell.className = 'emotion-score';
    scoreCell.id = `score-${emotion}`;
    scoreCell.textContent = score.toFixed(2);
    updateScoreColor(scoreCell, score);
    
    const barCell = document.createElement('td');
    const barContainer = document.createElement('div');
    barContainer.className = 'emotion-bar';
    const barFill = document.createElement('div');
    barFill.className = 'emotion-bar-fill';
    barFill.id = `bar-${emotion}`;
    barFill.style.width = `${score * 100}%`;
    updateBarColor(barFill, score);
    barContainer.appendChild(barFill);
    barCell.appendChild(barContainer);
    
    row.appendChild(nameCell);
    row.appendChild(scoreCell);
    row.appendChild(barCell);
    
    return row;
}

/**
 * Update score text color based on value
 */
function updateScoreColor(element, score) {
    element.classList.remove('score-low', 'score-medium', 'score-high');
    
    if (score < 0.33) {
        element.classList.add('score-low');
    } else if (score < 0.66) {
        element.classList.add('score-medium');
    } else {
        element.classList.add('score-high');
    }
}

/**
 * Update bar color based on value
 */
function updateBarColor(element, score) {
    element.classList.remove('bar-low', 'bar-medium', 'bar-high');
    
    if (score < 0.33) {
        element.classList.add('bar-low');
    } else if (score < 0.66) {
        element.classList.add('bar-medium');
    } else {
        element.classList.add('bar-high');
    }
}

/**
 * Update emotion display with new scores
 */
function updateEmotions(emotions) {
    Object.keys(emotions).forEach(emotion => {
        const score = emotions[emotion];
        const previousScore = emotionData[emotion] || 0;
        
        // Update stored data
        emotionData[emotion] = score;
        
        // Update score text
        const scoreElement = document.getElementById(`score-${emotion}`);
        if (scoreElement) {
            scoreElement.textContent = score.toFixed(2);
            updateScoreColor(scoreElement, score);
            
            // Add flash animation if score changed significantly
            if (Math.abs(score - previousScore) > 0.1) {
                const row = document.getElementById(`emotion-${emotion}`);
                if (row) {
                    row.classList.add('emotion-updated');
                    setTimeout(() => row.classList.remove('emotion-updated'), 500);
                }
            }
        }
        
        // Update bar
        const barElement = document.getElementById(`bar-${emotion}`);
        if (barElement) {
            barElement.style.width = `${score * 100}%`;
            updateBarColor(barElement, score);
        }
    });
    
    // Update timestamp
    const now = new Date();
    timestamp.textContent = `Last update: ${now.toLocaleTimeString()}`;
}

/**
 * Setup WebSocket connection
 */
function setupWebSocket() {
    console.log('Connecting to WebSocket...');
    socket = io();
    
    // Connection events
    socket.on('connect', () => {
        console.log('WebSocket connected');
        wsStatus.textContent = 'Connected';
        wsStatus.style.color = '#4caf50';
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        wsStatus.textContent = 'Disconnected';
        wsStatus.style.color = '#f44336';
    });
    
    socket.on('connection_response', (data) => {
        console.log('Connection response:', data);
    });
    
    // Emotion updates
    socket.on('emotion_update', (data) => {
        if (data.emotions) {
            updateEmotions(data.emotions);
        }
    });
    
    // Tracking responses
    socket.on('tracking_response', (data) => {
        console.log('Tracking response:', data);
        
        if (data.success) {
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'error');
        }
    });
    
    // Error handling
    socket.on('error', (data) => {
        console.error('Socket error:', data);
        showNotification(data.message || 'An error occurred', 'error');
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    startBtn.addEventListener('click', startTracking);
    stopBtn.addEventListener('click', stopTracking);
}

/**
 * Start emotion tracking
 */
function startTracking() {
    console.log('Starting tracking...');
    
    if (socket && socket.connected) {
        socket.emit('start_tracking');
        
        // Update UI
        isTracking = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'Active';
        
        // Start video feed
        startVideoFeed();
        
        showNotification('Tracking started - Please allow camera and microphone access', 'success');
    } else {
        showNotification('Not connected to server', 'error');
    }
}

/**
 * Stop emotion tracking
 */
function stopTracking() {
    console.log('Stopping tracking...');
    
    if (socket && socket.connected) {
        socket.emit('stop_tracking');
        
        // Update UI
        isTracking = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'Inactive';
        
        // Stop video feed
        stopVideoFeed();
        
        showNotification('Tracking stopped', 'success');
    } else {
        showNotification('Not connected to server', 'error');
    }
}

/**
 * Start video feed
 */
function startVideoFeed() {
    console.log('Starting video feed...');
    
    // Hide placeholder, show video
    videoPlaceholder.style.display = 'none';
    videoFeed.style.display = 'block';
    
    // Set video source to streaming endpoint
    videoFeed.src = '/video_feed?' + new Date().getTime();
    
    // Handle video load errors
    videoFeed.onerror = function() {
        console.error('Error loading video feed');
        showNotification('Video feed error - check camera permissions', 'error');
    };
}

/**
 * Stop video feed
 */
function stopVideoFeed() {
    console.log('Stopping video feed...');
    
    // Stop video by clearing source
    videoFeed.src = '';
    
    // Show placeholder, hide video
    videoFeed.style.display = 'none';
    videoPlaceholder.style.display = 'flex';
}

/**
 * Show notification message
 */
function showNotification(message, type) {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : '#f44336'};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Get current emotions on demand
 */
function getCurrentEmotions() {
    if (socket && socket.connected && isTracking) {
        socket.emit('get_current_emotions');
    }
}

/**
 * Check system status
 */
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        console.log('System status:', data);
        return data;
    } catch (error) {
        console.error('Error checking status:', error);
        return null;
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (isTracking) {
        stopTracking();
    }
});

// Export for debugging
window.emotionTracker = {
    getCurrentEmotions,
    checkStatus,
    emotionData,
    socket
};


