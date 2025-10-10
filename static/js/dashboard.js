/**
 * AI Emotion Tracking System - Dashboard JavaScript
 * Handles WebSocket communication and real-time UI updates
 */

// State management
let socket = null;
let isTracking = false;
let emotionData = {};
let emotionTimeline = null;
let settingsManager = null;
let previousDominantEmotion = null;
let emotionHistory = []; // For stability calculation

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
    
    uiLogger.info('Application initializing');
    
    // Initialize emotion table
    initEmotionTable();
    
    // Initialize timeline
    emotionTimeline = new EmotionTimeline('emotionTimeline');
    
    // Initialize settings manager
    settingsManager = new SettingsManager();
    
    // Setup WebSocket connection
    setupWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup table filters
    setupTableFilters();
    
    // Setup modals
    setupModals();
    
    console.log('Initialization complete');
    uiLogger.info('Application initialized successfully');
}

/**
 * Initialize the emotion table with all emotions
 */
function initEmotionTable() {
    emotionTableBody.innerHTML = '';
    
    // Get all emotions from metadata
    const allEmotions = Object.keys(EmotionMetadata.emotions);
    emotionCount.textContent = allEmotions.length;
    
    allEmotions.forEach(emotion => {
        const row = createEmotionRow(emotion, 0.0);
        emotionTableBody.appendChild(row);
        emotionData[emotion] = 0.0;
    });
}

/**
 * Create a table row for an emotion
 */
function createEmotionRow(emotion, score) {
    const meta = EmotionMetadata.getMetadata(emotion);
    
    const row = document.createElement('tr');
    row.id = `emotion-${emotion}`;
    row.setAttribute('data-group', meta.group);
    row.setAttribute('data-category', meta.category);
    
    const nameCell = document.createElement('td');
    nameCell.className = 'emotion-name';
    nameCell.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    nameCell.setAttribute('data-tippy-content', meta.definition);
    
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
    // Update chat emotions if chat module is loaded
    if (window.chatModule && window.chatModule.updateChatEmotions) {
        window.chatModule.updateChatEmotions(emotions);
    }
    
    // Add to emotion history for stability calculation
    emotionHistory.push(emotions);
    if (emotionHistory.length > 20) {
        emotionHistory.shift();
    }
    
    // Update summary card
    updateSummaryCard(emotions);
    
    // Update timeline
    if (emotionTimeline) {
        emotionTimeline.addDataPoint(emotions);
    }
    
    Object.keys(emotions).forEach(emotion => {
        const score = emotions[emotion];
        const previousScore = emotionData[emotion] || 0;
        
        // Update stored data
        emotionData[emotion] = score;
        
        // Update score text
        const scoreElement = document.getElementById(`score-${emotion}`);
        if (scoreElement) {
            DOMUtils.updateText(scoreElement, score.toFixed(2));
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

/**
 * Update summary card with dominant emotion
 */
function updateSummaryCard(emotions) {
    // Find dominant emotion
    let maxEmotion = null;
    let maxScore = 0;
    
    Object.entries(emotions).forEach(([emotion, score]) => {
        if (score > maxScore) {
            maxScore = score;
            maxEmotion = emotion;
        }
    });
    
    if (!maxEmotion) return;
    
    // Update name and score in emotion indicator
    const dominantName = document.getElementById('dominantName');
    const dominantScore = document.getElementById('dominantScore');
    
    if (dominantName) DOMUtils.updateText(dominantName, maxEmotion.charAt(0).toUpperCase() + maxEmotion.slice(1));
    if (dominantScore) DOMUtils.updateText(dominantScore, maxScore.toFixed(2));
}

/**
 * Update emotion trend indicator
 */
function updateEmotionTrend(emotion, score) {
    const trendArrow = document.querySelector('.trend-arrow');
    const trendText = document.querySelector('.trend-text');
    
    if (previousDominantEmotion && previousDominantEmotion.emotion === emotion) {
        const previousScore = previousDominantEmotion.score;
        const diff = score - previousScore;
        
        if (diff > 0.05) {
            if (trendArrow) trendArrow.textContent = '↑';
            if (trendText) trendText.textContent = 'Rising';
        } else if (diff < -0.05) {
            if (trendArrow) trendArrow.textContent = '↓';
            if (trendText) trendText.textContent = 'Declining';
        } else {
            if (trendArrow) trendArrow.textContent = '→';
            if (trendText) trendText.textContent = 'Stable';
        }
    } else {
        if (trendArrow) trendArrow.textContent = '↗';
        if (trendText) trendText.textContent = 'Changed';
    }
    
    previousDominantEmotion = { emotion, score };
}

/**
 * Update stability badge based on emotion variance
 */
function updateStabilityBadge() {
    if (emotionHistory.length < 5) return;
    
    // Calculate variance of dominant emotion
    const recentScores = emotionHistory.slice(-10).map(emotions => {
        let maxScore = 0;
        Object.values(emotions).forEach(score => {
            if (score > maxScore) maxScore = score;
        });
        return maxScore;
    });
    
    const mean = recentScores.reduce((a, b) => a + b) / recentScores.length;
    const variance = recentScores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / recentScores.length;
    const stdDev = Math.sqrt(variance);
    
    const badgeText = document.querySelector('#stabilityBadge .badge-text');
    
    if (stdDev < 0.1) {
        if (badgeText) badgeText.textContent = 'Very Stable';
    } else if (stdDev < 0.2) {
        if (badgeText) badgeText.textContent = 'Stable';
    } else {
        if (badgeText) badgeText.textContent = 'Fluctuating';
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    // Start tracking (S)
    DOMUtils.addShortcut('s', () => {
        if (!isTracking) startTracking();
    });
    
    // Stop tracking (X)
    DOMUtils.addShortcut('x', () => {
        if (isTracking) stopTracking();
    });
    
    // Open settings (,)
    DOMUtils.addShortcut(',', () => {
        if (settingsManager) settingsManager.open();
    });
    
    // Open help (?)
    DOMUtils.addShortcut('?', () => {
        const helpModal = document.getElementById('helpModal');
        if (helpModal) {
            helpModal.style.display = 'flex';
            helpModal.setAttribute('aria-hidden', 'false');
        }
    });
    
    uiLogger.info('Keyboard shortcuts initialized');
}

/**
 * Setup table filters
 */
function setupTableFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            filterTable(filter);
        });
    });
    
    // Initialize tooltips using Tippy.js
    if (typeof tippy !== 'undefined') {
        tippy('[data-tippy-content]', {
            theme: 'dark',
            placement: 'top',
            arrow: true,
            animation: 'fade'
        });
    }
}

/**
 * Filter emotion table by group
 */
function filterTable(filter) {
    const rows = document.querySelectorAll('#emotionTableBody tr');
    
    rows.forEach(row => {
        if (filter === 'all') {
            row.style.display = '';
        } else {
            const group = row.getAttribute('data-group');
            row.style.display = group === filter ? '' : 'none';
        }
    });
}

/**
 * Setup modals
 */
function setupModals() {
    // Settings modal
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            if (settingsManager) {
                settingsManager.open();
                settingsManager.setSocket(socket);
            }
        });
    }
    
    // Help modal
    const helpBtn = document.getElementById('helpBtn');
    const helpModal = document.getElementById('helpModal');
    const closeHelpBtns = document.querySelectorAll('.close-help');
    
    if (helpBtn && helpModal) {
        helpBtn.addEventListener('click', () => {
            helpModal.style.display = 'flex';
            helpModal.setAttribute('aria-hidden', 'false');
        });
        
        closeHelpBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                helpModal.style.display = 'none';
                helpModal.setAttribute('aria-hidden', 'true');
            });
        });
        
        // Close on outside click
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                helpModal.style.display = 'none';
                helpModal.setAttribute('aria-hidden', 'true');
            }
        });
    }
    
    // Clear timeline button
    const clearTimelineBtn = document.getElementById('clearTimelineBtn');
    if (clearTimelineBtn) {
        clearTimelineBtn.addEventListener('click', () => {
            if (emotionTimeline) {
                emotionTimeline.clear();
                DOMUtils.announce('Timeline cleared');
            }
        });
    }
}

// Export for debugging
window.emotionTracker = {
    getCurrentEmotions,
    checkStatus,
    emotionData,
    socket,
    emotionTimeline,
    settingsManager
};


