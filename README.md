# AI Emotion Tracking System 🧠

A real-time cognitive and emotional state tracking system that analyzes live video and audio inputs to assess user emotions, mood, awareness, and receptiveness. The system uses advanced AI models to detect 25-30 different emotions and displays them on an elegant web-based dashboard with real-time updates.

![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)
![WebSocket](https://img.shields.io/badge/websocket-real--time-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🎯 Features

- **Real-time Emotion Detection**: Analyzes facial expressions and speech patterns
- **Multimodal Analysis**: Combines video and audio data for comprehensive emotion profiling
- **30 Emotion Categories**: Tracks basic emotions plus complex states like receptiveness, awareness, trust, and more
- **Web Dashboard**: Beautiful, responsive interface with live updates
- **Apple M3 Optimized**: Leverages Metal Performance Shaders (MPS) for GPU acceleration
- **Low Latency**: Updates every 0.5 seconds for smooth real-time tracking
- **Temporal Smoothing**: Reduces jitter for stable emotion readings

## 📊 Tracked Emotions

### Visual Emotions (from facial analysis)
- Happy, Sad, Angry, Fear, Surprise, Disgust, Neutral

### Vocal Emotions (from speech analysis)
- Calm, Excited, Frustrated, Engaged, Confused, Anxious, Confident, Interested, Bored, Curious, Stressed

### Derived/Composite Emotions
- **Receptiveness**: Engagement + positive emotions
- **Awareness**: Attention indicators
- **Trust**: Calm + happy + confident
- **Anticipation**: Excited + curious
- **Relaxed**: Calm + neutral
- **Skeptical**: Confused + neutral
- **Distracted**: Inverse of engaged
- **Enthusiastic**: Excited + happy
- **Contemplative**: Neutral + interested
- **Alert**: Awareness + surprise

## 🏗️ Architecture

```
┌─────────────────┐
│   Webcam Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Video Processor │─────▶│  Emotion Fusion  │
│   (DeepFace)    │      │     Engine       │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
┌─────────────────┐      ┌──────────────────┐
│ Microphone Input│      │  Flask + Socket  │
└────────┬────────┘      │       IO         │
         │               └────────┬─────────┘
         ▼                        │
┌─────────────────┐               │
│ Audio Processor │───────────────┘
│   (Wav2Vec2)    │               
└─────────────────┘               
                                  
         WebSocket Updates
                │
                ▼
        ┌──────────────┐
        │   Dashboard  │
        │  (Browser)   │
        └──────────────┘
```

## 🚀 Installation

### Prerequisites

- **Python 3.11** (recommended)
- **macOS** with Apple M3 chip (optimized for MPS)
- **Webcam** and **Microphone** access
- **Homebrew** (for installing system dependencies)

### System Dependencies

```bash
# Install PortAudio (required for PyAudio)
brew install portaudio

# Install FFmpeg (required for audio processing)
brew install ffmpeg
```

### Project Setup

1. **Clone or navigate to the project directory**

```bash
cd "/Users/abhinav/Desktop/Personal Projects/Project"
```

2. **Create virtual environment**

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
```

3. **Install Python dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installation may take 5-10 minutes as it downloads pre-trained models (~1-2GB).

### Troubleshooting Installation

#### PyAudio Installation Issues

If PyAudio fails to install:

```bash
# Install with Homebrew portaudio
brew install portaudio
pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio
```

#### TensorFlow/PyTorch Issues

Ensure you have the latest versions compatible with Apple Silicon:

```bash
pip install --upgrade torch tensorflow
```

## 🎮 Usage

### Starting the System

1. **Activate virtual environment** (if not already activated)

```bash
source .venv311/bin/activate
```

2. **Navigate to src directory**

```bash
cd src
```

3. **Run the application**

```bash
python app.py
```

4. **Open your browser**

Navigate to: `http://localhost:5000`

### Using the Dashboard

1. **Click "Start Tracking"** to begin emotion detection
2. **Allow camera and microphone access** when prompted by your browser
3. **View real-time emotion scores** updating every 0.5 seconds
4. **Monitor the table** showing all 30 emotions with values from 0.00 to 1.00
5. **Click "Stop Tracking"** when finished

### Browser Permissions

The system requires:
- **Camera access**: For facial emotion recognition
- **Microphone access**: For speech emotion recognition

Make sure to allow these permissions when prompted.

## 📁 Project Structure

```
Project/
├── src/
│   ├── app.py                 # Flask server with WebSocket
│   ├── video_processor.py     # Facial emotion recognition
│   ├── audio_processor.py     # Speech emotion recognition
│   ├── emotion_fusion.py      # Multimodal emotion fusion
│   └── config.py              # Configuration settings
├── static/
│   ├── css/
│   │   └── style.css          # Dashboard styling
│   └── js/
│       └── dashboard.js       # Real-time UI updates
├── templates/
│   └── index.html             # Main dashboard interface
├── logs/
│   ├── emotion_tracker.log    # Application logs
│   └── errors.log             # Error logs
├── .venv311/                  # Virtual environment
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

### Video Settings

```python
VIDEO_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30,
    'camera_index': 0,  # Change if using external webcam
}
```

### Audio Settings

```python
AUDIO_CONFIG = {
    'sample_rate': 16000,
    'channels': 1,
    'chunk_duration': 1.0,  # Seconds per chunk
}
```

### Processing Settings

```python
PROCESSING_CONFIG = {
    'update_frequency': 0.5,        # Update every 0.5 seconds
    'video_enabled': True,
    'audio_enabled': True,
    'temporal_smoothing_alpha': 0.3,  # 0-1, higher = less smoothing
}
```

### Emotion Fusion Weights

```python
FUSION_WEIGHTS = {
    'video': 0.5,  # 50% weight for visual emotions
    'audio': 0.5,  # 50% weight for audio emotions
}
```

## 🔬 Technical Details

### Models Used

1. **DeepFace** (Facial Emotion Recognition)
   - Pre-trained CNN model
   - Detects: happy, sad, angry, fear, surprise, disgust, neutral
   - Framework: TensorFlow

2. **Wav2Vec2** (Speech Emotion Recognition)
   - Pre-trained transformer model from Hugging Face
   - Model: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`
   - Framework: PyTorch

### Performance Optimization

- **Apple M3 MPS**: GPU acceleration via Metal Performance Shaders
- **Threaded Processing**: Video and audio processed in separate threads
- **Frame Skipping**: Processes every Nth frame to reduce CPU load
- **Temporal Smoothing**: Exponential moving average prevents jitter

### Expected Performance

- **Latency**: 0.5-1 second update rate
- **FPS**: 15-30 frames processed per second
- **CPU Usage**: < 30% on Apple M3
- **Memory**: < 1GB RAM
- **GPU Usage**: Moderate (MPS acceleration)

## 🐛 Troubleshooting

### Camera Not Working

**Issue**: "Failed to open webcam" error

**Solutions**:
- Check if another application is using the camera
- Grant camera permissions in System Preferences → Privacy & Security → Camera
- Try changing `camera_index` in config.py (0, 1, 2, etc.)

### Microphone Not Working

**Issue**: No audio emotions detected

**Solutions**:
- Grant microphone permissions in System Preferences → Privacy & Security → Microphone
- Check microphone is working in System Preferences → Sound → Input
- Ensure PyAudio installed correctly with PortAudio support

### WebSocket Connection Failed

**Issue**: Dashboard shows "Disconnected"

**Solutions**:
- Ensure Flask server is running
- Check firewall settings
- Try accessing `http://127.0.0.1:5000` instead of localhost
- Restart the server

### Model Download Issues

**Issue**: Models fail to download on first run

**Solutions**:
- Ensure stable internet connection
- Models are downloaded automatically on first run (may take 5-10 minutes)
- Check logs in `logs/emotion_tracker.log` for specific errors

### High CPU/Memory Usage

**Solutions**:
- Reduce FPS in config.py
- Increase update_frequency (e.g., 1.0 second)
- Disable video or audio processing if only one modality needed
- Close other applications

### No Face Detected

**Issue**: Video emotions stuck at neutral

**Solutions**:
- Ensure adequate lighting
- Position face clearly in camera view
- Check `enforce_detection` setting in video_processor.py
- Camera may need to adjust exposure (wait a few seconds)

## 📊 Logs

Logs are stored in the `logs/` directory:

- **emotion_tracker.log**: General application logs
- **errors.log**: Error and exception logs

To view logs in real-time:

```bash
tail -f logs/emotion_tracker.log
```

## 🔒 Privacy & Security

- **Local Processing**: All processing happens locally on your machine
- **No Data Storage**: Emotion data is not saved or transmitted externally
- **No Recording**: Video and audio are processed in real-time, not recorded
- **Browser Permissions**: You control camera/microphone access

## 🛠️ Development

### Running in Debug Mode

Edit `src/config.py`:

```python
FLASK_CONFIG = {
    'debug': True,  # Enable debug mode
}
```

### Adding New Emotions

1. Add emotion name to `EMOTION_LIST` in `config.py`
2. Update derivation logic in `emotion_fusion.py`
3. Restart the application

### Testing

```bash
# Test video processor
python -c "from video_processor import VideoProcessor; vp = VideoProcessor(); vp.start()"

# Test audio processor
python -c "from audio_processor import AudioProcessor; ap = AudioProcessor(); ap.start()"

# Check system status
curl http://localhost:5000/api/status
```

## 📚 Dependencies

Key dependencies:

- **Flask 3.0.0**: Web framework
- **Flask-SocketIO 5.3.5**: Real-time WebSocket communication
- **OpenCV 4.8.1.78**: Video capture and processing
- **DeepFace 0.0.79**: Facial emotion recognition
- **Transformers 4.35.0**: Wav2Vec2 model
- **PyTorch 2.1.0**: Deep learning framework (MPS support)
- **Librosa 0.10.1**: Audio feature extraction
- **PyAudio 0.2.14**: Audio capture
- **NumPy 1.24.3**: Numerical processing

## 🎓 References

- [DeepFace](https://github.com/serengil/deepface) - Facial emotion recognition
- [Wav2Vec2](https://huggingface.co/ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition) - Speech emotion model
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - WebSocket communication
- [Apple MPS](https://developer.apple.com/metal/pytorch/) - GPU acceleration

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues, questions, or suggestions:

1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Open an issue with detailed description

## 🎉 Acknowledgments

Built with cutting-edge AI models from:
- Meta AI (Wav2Vec2)
- DeepFace community
- Hugging Face Transformers
- OpenCV contributors

---

**Made with ❤️ for emotion AI research**

*Optimized for Apple Silicon M3 • Real-time Performance • Privacy-First Design*


