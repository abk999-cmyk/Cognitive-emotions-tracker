# Quick Start Guide 🚀

Get up and running with the AI Emotion Tracking System in minutes!

## Prerequisites Check

- ✅ **Python 3.11** installed
- ✅ **macOS** with Apple M3 chip
- ✅ **Webcam** and **Microphone** available
- ✅ **10GB** free disk space (for models)

## Installation (First Time Only)

### 1. Install System Dependencies

```bash
# Install PortAudio for audio capture
brew install portaudio

# Install FFmpeg for audio processing (optional)
brew install ffmpeg
```

### 2. Setup Python Environment

```bash
# Navigate to project directory
cd "/Users/abhinav/Desktop/Personal Projects/Project"

# Create virtual environment (already done if you see .venv311 folder)
python3.11 -m venv .venv311

# Activate virtual environment
source .venv311/bin/activate

# Install dependencies (takes 5-10 minutes)
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using the Start Script (Recommended)

```bash
./start.sh
```

### Option 2: Manual Start

```bash
# Activate virtual environment
source .venv311/bin/activate

# Navigate to src directory
cd src

# Start the server
python app.py
```

## Using the Dashboard

1. **Open your browser** to: http://localhost:5000

2. **Click "Start Tracking"**

3. **Allow permissions** for camera and microphone when prompted

4. **View real-time emotions** in the table (updates every 0.5 seconds)

5. **Click "Stop Tracking"** when finished

## Common Issues & Solutions

### Issue: "Failed to open webcam"

**Solution:**
- Check if another app is using the camera
- Grant camera permissions: System Preferences → Privacy & Security → Camera
- Try changing `camera_index` in `src/config.py`

### Issue: "PyAudio installation failed"

**Solution:**
```bash
# Install PortAudio first
brew install portaudio

# Then install PyAudio with correct flags
CFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install pyaudio
```

### Issue: "No module named 'deepface'"

**Solution:**
```bash
source .venv311/bin/activate
pip install -r requirements.txt
```

### Issue: High CPU usage

**Solution:**
Edit `src/config.py`:
```python
VIDEO_CONFIG = {
    'fps': 15,  # Reduce from 30
}

PROCESSING_CONFIG = {
    'update_frequency': 1.0,  # Increase from 0.5
}
```

### Issue: Models downloading slowly

**Solution:**
- Models download automatically on first run (~1-2GB)
- Ensure stable internet connection
- Wait patiently (5-10 minutes for first run)
- Models are cached in `~/.deepface/` and `~/.cache/`

## First Run Notes

### What Happens on First Run?

1. **Model Downloads** (5-10 minutes)
   - DeepFace facial emotion models (~500MB)
   - Wav2Vec2 speech emotion model (~1.2GB)

2. **Model Cache Location**
   - `~/.deepface/weights/` - Facial models
   - `~/.cache/huggingface/` - Speech models

3. **Initialization**
   - TensorFlow/PyTorch GPU setup
   - MPS (Metal) backend initialization
   - Camera/microphone access permissions

### Expected First Run Timeline

```
0:00 - Flask server starts
0:05 - Click "Start Tracking"
0:10 - Model downloads begin (if first time)
5:00 - Models loading into memory
5:30 - Camera/microphone initialization
6:00 - First emotion scores appear! 🎉
```

## Performance Tips

### For Best Performance

1. **Close unnecessary apps** to free RAM

2. **Good lighting** for better facial detection

3. **Quiet environment** for better speech analysis

4. **Stable position** - keep face in camera view

### Optimization Settings

Edit `src/config.py` for your needs:

```python
# For lower CPU usage
VIDEO_CONFIG = {'fps': 15}
PROCESSING_CONFIG = {'update_frequency': 1.0}

# For higher accuracy (more CPU)
VIDEO_CONFIG = {'fps': 30}
PROCESSING_CONFIG = {'update_frequency': 0.3}
```

## File Locations

| Item | Location |
|------|----------|
| **Logs** | `logs/emotion_tracker.log` |
| **Config** | `src/config.py` |
| **Dashboard** | `templates/index.html` |
| **Models** | `~/.deepface/` and `~/.cache/` |

## Stopping the Application

### Graceful Shutdown

1. **In Browser**: Click "Stop Tracking"
2. **In Terminal**: Press `Ctrl+C`

The system will:
- Stop video/audio capture
- Release camera/microphone
- Clean up resources
- Save logs

## Testing the Installation

```bash
# Quick dependency check
source .venv311/bin/activate
python -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"
```

Should output: `MPS Available: True`

## Next Steps

- 📖 Read the full **README.md** for detailed documentation
- ⚙️ Customize settings in **src/config.py**
- 🎨 Modify the dashboard in **templates/index.html**
- 📊 Add custom emotions in **src/emotion_fusion.py**

## Getting Help

1. **Check logs**: `tail -f logs/emotion_tracker.log`
2. **Verify installation**: See testing section above
3. **Review README**: Detailed troubleshooting guide
4. **Check configuration**: Verify `src/config.py` settings

## System Requirements

### Minimum
- **CPU**: Apple M3
- **RAM**: 8GB
- **Storage**: 10GB free
- **OS**: macOS 12.0+
- **Internet**: Required for first run

### Recommended
- **RAM**: 16GB
- **Storage**: 15GB free
- **Internet**: Broadband connection

---

**Ready to start?** Run `./start.sh` and open http://localhost:5000! 🚀

*For detailed information, see README.md*


