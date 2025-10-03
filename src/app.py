"""
Flask Application with SocketIO for Real-Time Emotion Tracking
Main server that coordinates video/audio processing and serves dashboard
"""

import sys
import os
import logging
import time
import threading
import cv2
from flask import Flask, render_template, jsonify, Response
from flask_socketio import SocketIO, emit

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_processor import VideoProcessor
from audio_processor import AudioProcessor
from emotion_fusion import EmotionFusion
from openai_chat import EmotionAwareChatbot
from config import (
    FLASK_CONFIG,
    PROCESSING_CONFIG,
    LOGGING_CONFIG,
    EMOTION_LIST
)

# Setup logging
os.makedirs(os.path.dirname(LOGGING_CONFIG['log_file']), exist_ok=True)
logging.basicConfig(
    filename=LOGGING_CONFIG['log_file'],
    level=LOGGING_CONFIG['log_level'],
    format=LOGGING_CONFIG['log_format']
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)
app.config['SECRET_KEY'] = 'emotion-tracker-secret-key-2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global components
video_processor = None
audio_processor = None
emotion_fusion = None
chatbot = None
tracking_active = False
emission_thread = None


def initialize_processors():
    """Initialize all processing components"""
    global video_processor, audio_processor, emotion_fusion, chatbot
    
    try:
        logger.info("Initializing emotion tracking system...")
        
        # Create processors
        video_processor = VideoProcessor()
        audio_processor = AudioProcessor()
        emotion_fusion = EmotionFusion()
        chatbot = EmotionAwareChatbot()
        
        logger.info("Processors initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize processors: {e}")
        return False


def emit_emotion_updates():
    """Background thread that emits emotion updates via WebSocket"""
    global tracking_active
    
    logger.info("Emotion update emission thread started")
    
    while tracking_active:
        try:
            # Get emotions from both processors
            video_emotions = video_processor.get_emotions() if video_processor else {}
            audio_emotions = audio_processor.get_emotions() if audio_processor else {}
            
            # Fuse emotions
            if emotion_fusion:
                all_emotions = emotion_fusion.get_all_emotions(video_emotions, audio_emotions)
            else:
                all_emotions = {emotion: 0.0 for emotion in EMOTION_LIST}
            
            # Emit to all connected clients
            socketio.emit('emotion_update', {
                'emotions': all_emotions,
                'timestamp': time.time()
            })
            
            # Wait before next update
            time.sleep(PROCESSING_CONFIG['update_frequency'])
            
        except Exception as e:
            logger.error(f"Error in emission thread: {e}")
            time.sleep(1.0)
    
    logger.info("Emotion update emission thread stopped")


@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html', emotions=EMOTION_LIST)


@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        'tracking_active': tracking_active,
        'video_enabled': PROCESSING_CONFIG['video_enabled'],
        'audio_enabled': PROCESSING_CONFIG['audio_enabled'],
        'emotion_count': len(EMOTION_LIST)
    })


@app.route('/api/emotions')
def get_emotions():
    """Get current emotion scores (REST endpoint)"""
    try:
        video_emotions = video_processor.get_emotions() if video_processor else {}
        audio_emotions = audio_processor.get_emotions() if audio_processor else {}
        
        if emotion_fusion:
            all_emotions = emotion_fusion.get_all_emotions(video_emotions, audio_emotions)
        else:
            all_emotions = {emotion: 0.0 for emotion in EMOTION_LIST}
        
        return jsonify({
            'success': True,
            'emotions': all_emotions,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting emotions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_video_frames():
    """Generator function to yield video frames with face mesh overlay"""
    while True:
        try:
            if video_processor and tracking_active:
                # Get current frame with mesh overlay
                frame = video_processor.get_current_frame()
                
                if frame is not None:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    if ret:
                        frame_bytes = buffer.tobytes()
                        # Yield frame in multipart format
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # If no frame available, wait a bit
                    time.sleep(0.033)  # ~30 FPS
            else:
                # If not tracking, wait
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error generating video frame: {e}")
            time.sleep(0.1)


@app.route('/video_feed')
def video_feed():
    """Video streaming route with face mesh overlay"""
    return Response(
        generate_video_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected")
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected")


@socketio.on('start_tracking')
def handle_start_tracking():
    """Start emotion tracking"""
    global tracking_active, emission_thread
    
    try:
        if tracking_active:
            emit('tracking_response', {
                'success': False,
                'message': 'Tracking already active'
            })
            return
        
        logger.info("Starting emotion tracking...")
        
        # Initialize processors if not done
        if not video_processor or not audio_processor:
            if not initialize_processors():
                emit('tracking_response', {
                    'success': False,
                    'message': 'Failed to initialize processors'
                })
                return
        
        # Start processors
        if PROCESSING_CONFIG['video_enabled'] and video_processor:
            video_processor.start()
            logger.info("Video processor started")
        
        if PROCESSING_CONFIG['audio_enabled'] and audio_processor:
            audio_processor.start()
            logger.info("Audio processor started")
        
        # Start emission thread
        tracking_active = True
        emission_thread = threading.Thread(target=emit_emotion_updates, daemon=True)
        emission_thread.start()
        
        emit('tracking_response', {
            'success': True,
            'message': 'Tracking started successfully'
        })
        
        logger.info("Emotion tracking started successfully")
        
    except Exception as e:
        logger.error(f"Error starting tracking: {e}")
        emit('tracking_response', {
            'success': False,
            'message': f'Error: {str(e)}'
        })


@socketio.on('stop_tracking')
def handle_stop_tracking():
    """Stop emotion tracking"""
    global tracking_active
    
    try:
        if not tracking_active:
            emit('tracking_response', {
                'success': False,
                'message': 'Tracking not active'
            })
            return
        
        logger.info("Stopping emotion tracking...")
        
        # Stop emission thread
        tracking_active = False
        
        # Stop processors
        if video_processor:
            video_processor.stop()
            logger.info("Video processor stopped")
        
        if audio_processor:
            audio_processor.stop()
            logger.info("Audio processor stopped")
        
        # Reset fusion state
        if emotion_fusion:
            emotion_fusion.reset()
        
        emit('tracking_response', {
            'success': True,
            'message': 'Tracking stopped successfully'
        })
        
        logger.info("Emotion tracking stopped successfully")
        
    except Exception as e:
        logger.error(f"Error stopping tracking: {e}")
        emit('tracking_response', {
            'success': False,
            'message': f'Error: {str(e)}'
        })


@socketio.on('get_current_emotions')
def handle_get_current_emotions():
    """Get current emotion state on demand"""
    try:
        video_emotions = video_processor.get_emotions() if video_processor else {}
        audio_emotions = audio_processor.get_emotions() if audio_processor else {}
        
        if emotion_fusion:
            all_emotions = emotion_fusion.get_all_emotions(video_emotions, audio_emotions)
        else:
            all_emotions = {emotion: 0.0 for emotion in EMOTION_LIST}
        
        emit('emotion_update', {
            'emotions': all_emotions,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting current emotions: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# CHAT API ROUTES
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the emotion-aware AI assistant"""
    try:
        from flask import request
        
        # Get request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        
        # Get current emotions
        video_emotions = video_processor.get_emotions() if video_processor else {}
        audio_emotions = audio_processor.get_emotions() if audio_processor else {}
        
        if emotion_fusion:
            current_emotions = emotion_fusion.get_all_emotions(video_emotions, audio_emotions)
        else:
            current_emotions = {emotion: 0.0 for emotion in EMOTION_LIST}
        
        # Initialize chatbot if not done
        global chatbot
        if not chatbot:
            chatbot = EmotionAwareChatbot()
        
        # Send message to chatbot with emotion context
        result = chatbot.send_message(user_message, current_emotions)
        
        if result['success']:
            logger.info(f"Chat response generated with tone: {result.get('tone_used', 'unknown')}")
            return jsonify(result)
        else:
            logger.error(f"Chat error: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': "I apologize, but I'm experiencing technical difficulties. Please try again."
        }), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get conversation history"""
    try:
        if chatbot:
            history = chatbot.get_conversation_history()
            return jsonify({
                'success': True,
                'history': history,
                'count': len(history)
            })
        else:
            return jsonify({
                'success': True,
                'history': [],
                'count': 0
            })
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat/reset', methods=['DELETE'])
def reset_chat():
    """Clear conversation history"""
    try:
        if chatbot:
            chatbot.clear_history()
            logger.info("Chat history cleared")
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        })
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat/stats', methods=['GET'])
def get_chat_stats():
    """Get chatbot statistics"""
    try:
        if chatbot:
            stats = chatbot.get_stats()
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            return jsonify({
                'success': True,
                'stats': {
                    'messages_in_history': 0,
                    'messages_last_minute': 0
                }
            })
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def cleanup():
    """Cleanup function called on shutdown"""
    global tracking_active
    
    logger.info("Cleaning up resources...")
    tracking_active = False
    
    if video_processor:
        video_processor.stop()
    
    if audio_processor:
        audio_processor.stop()
    
    logger.info("Cleanup complete")


if __name__ == '__main__':
    try:
        logger.info("=" * 60)
        logger.info("AI Emotion Tracking System Starting")
        logger.info("=" * 60)
        
        print("\n" + "=" * 60)
        print("AI EMOTION TRACKING SYSTEM")
        print("=" * 60)
        print(f"Server starting on http://{FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}")
        print(f"Open your browser and navigate to http://localhost:{FLASK_CONFIG['port']}")
        print("=" * 60 + "\n")
        
        # Initialize processors on startup
        initialize_processors()
        
        # Run Flask-SocketIO server
        socketio.run(
            app,
            host=FLASK_CONFIG['host'],
            port=FLASK_CONFIG['port'],
            debug=FLASK_CONFIG['debug'],
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        cleanup()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFATAL ERROR: {e}")
        cleanup()


