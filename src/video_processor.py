"""
Video Processing Module for Facial Emotion Recognition
Uses OpenCV for video capture, DeepFace for emotion detection, and MediaPipe for face mesh
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import Dict, Optional, List, Tuple
from deepface import DeepFace
import mediapipe as mp
from config import VIDEO_CONFIG, PROCESSING_CONFIG, LOGGING_CONFIG, MESH_CONFIG

# Setup logging
logging.basicConfig(
    filename=LOGGING_CONFIG['log_file'],
    level=LOGGING_CONFIG['log_level'],
    format=LOGGING_CONFIG['log_format']
)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles real-time video capture, facial emotion recognition, and face mesh tracking"""
    
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.current_emotions = {}
        self.current_frame = None
        self.current_landmarks = []
        self.lock = threading.Lock()
        self.frame_lock = threading.Lock()
        self.last_successful_detection = None
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.face_mesh = None
        
    def initialize(self) -> bool:
        """Initialize video capture and face mesh"""
        try:
            self.cap = cv2.VideoCapture(VIDEO_CONFIG['camera_index'])
            
            if not self.cap.isOpened():
                logger.error("Failed to open webcam")
                return False
            
            # Set video properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_CONFIG['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_CONFIG['height'])
            self.cap.set(cv2.CAP_PROP_FPS, VIDEO_CONFIG['fps'])
            
            # Initialize MediaPipe Face Mesh
            if MESH_CONFIG['enabled']:
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,  # Enable iris tracking
                    min_detection_confidence=MESH_CONFIG['confidence_threshold'],
                    min_tracking_confidence=MESH_CONFIG['confidence_threshold']
                )
                logger.info("Face mesh initialized successfully")
            
            logger.info("Video capture initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing video capture: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Process a single frame and extract emotion scores
        
        Args:
            frame: BGR image frame from OpenCV
            
        Returns:
            Dictionary of emotion scores (0-1 range) or None if processing fails
        """
        try:
            # Analyze frame with DeepFace
            # enforce_detection=False allows processing even if no face detected
            result = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            # DeepFace returns a list, get first result
            if isinstance(result, list):
                result = result[0]
            
            # Extract emotion scores
            emotions = result.get('emotion', {})
            
            # Normalize scores to 0-1 range (DeepFace returns percentages)
            normalized_emotions = {
                emotion: score / 100.0 
                for emotion, score in emotions.items()
            }
            
            self.last_successful_detection = time.time()
            return normalized_emotions
            
        except Exception as e:
            logger.warning(f"Error processing frame: {e}")
            return None
    
    def get_emotions(self) -> Dict[str, float]:
        """Get current emotion scores (thread-safe)"""
        with self.lock:
            return self.current_emotions.copy()
    
    def process_face_mesh(self, frame: np.ndarray) -> Tuple[List[Tuple[int, int]], np.ndarray]:
        """
        Process frame with MediaPipe Face Mesh
        
        Args:
            frame: BGR image frame from OpenCV
            
        Returns:
            Tuple of (landmarks_list, annotated_frame)
        """
        landmarks_list = []
        annotated_frame = frame.copy()
        
        if not self.face_mesh or not MESH_CONFIG['enabled']:
            return landmarks_list, annotated_frame
        
        try:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Extract landmark coordinates
                    h, w, _ = frame.shape
                    for landmark in face_landmarks.landmark:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        landmarks_list.append((x, y))
                    
                    # Draw face mesh on frame
                    if MESH_CONFIG['show_tesselation']:
                        self.mp_drawing.draw_landmarks(
                            image=annotated_frame,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                color=MESH_CONFIG['color'],
                                thickness=MESH_CONFIG['thickness'],
                                circle_radius=0
                            )
                        )
                    
                    if MESH_CONFIG['show_contours']:
                        self.mp_drawing.draw_landmarks(
                            image=annotated_frame,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                color=(0, 255, 0),
                                thickness=1,
                                circle_radius=0
                            )
                        )
                    
                    if MESH_CONFIG['show_irises']:
                        self.mp_drawing.draw_landmarks(
                            image=annotated_frame,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_IRISES,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                color=(0, 255, 255),
                                thickness=1,
                                circle_radius=1
                            )
                        )
                    
                    # Draw landmark points
                    if MESH_CONFIG['show_landmarks']:
                        for x, y in landmarks_list:
                            cv2.circle(annotated_frame, (x, y), 
                                     MESH_CONFIG['circle_radius'], 
                                     (255, 255, 255), -1)
        
        except Exception as e:
            logger.warning(f"Error processing face mesh: {e}")
        
        return landmarks_list, annotated_frame
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get current frame with face mesh overlay (thread-safe)"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def get_landmarks(self) -> List[Tuple[int, int]]:
        """Get current face landmarks (thread-safe)"""
        with self.frame_lock:
            return self.current_landmarks.copy()
    
    def start(self):
        """Start video processing in a separate thread"""
        if not self.initialize():
            logger.error("Failed to initialize video processor")
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_thread.start()
        logger.info("Video processor started")
    
    def _process_loop(self):
        """Main processing loop (runs in separate thread)"""
        frame_skip = max(1, int(VIDEO_CONFIG['fps'] / (1.0 / PROCESSING_CONFIG['update_frequency'])))
        frame_count = 0
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from webcam")
                    time.sleep(0.1)
                    continue
                
                # Always process face mesh for video feed (every frame for smooth display)
                landmarks, annotated_frame = self.process_face_mesh(frame)
                
                # Store current frame with mesh overlay
                with self.frame_lock:
                    self.current_frame = annotated_frame
                    self.current_landmarks = landmarks
                
                # Process every Nth frame for emotion detection to reduce CPU usage
                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue
                
                # Process frame for emotions
                emotions = self.process_frame(frame)
                
                if emotions:
                    with self.lock:
                        self.current_emotions = emotions
                else:
                    # If processing fails, use default neutral state
                    with self.lock:
                        if not self.current_emotions:
                            self.current_emotions = {
                                'happy': 0.0,
                                'sad': 0.0,
                                'angry': 0.0,
                                'fear': 0.0,
                                'surprise': 0.0,
                                'disgust': 0.0,
                                'neutral': 1.0
                            }
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in video processing loop: {e}")
                time.sleep(0.1)
    
    def stop(self):
        """Stop video processing and release resources"""
        logger.info("Stopping video processor...")
        self.is_running = False
        
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        
        if self.face_mesh:
            self.face_mesh.close()
        
        logger.info("Video processor stopped")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame for display (optional)"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None


