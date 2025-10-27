# Audio to Video Converter

A simple Docker-based web application that converts audio files to MP4 videos with custom placeholder images from placehold.co.

## Features

- **Web UI**: Clean Bootstrap interface for easy file uploads
- **Audio Support**: MP3, WAV, OGG, M4A, FLAC, AAC
- **Custom Images**: Uses placehold.co with your custom text
- **Smart Naming**: Output filename matches your image text (spaces replaced with underscores)
- **Brand Colors**: Uses Cabernet (#670038) theme

## Quick Start

### 1. Build and Run

```bash
docker-compose up -d
```

### 2. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Convert Audio to Video

1. Upload your audio file
2. Enter text for the video image (e.g., "My Podcast Episode")
3. Click "Convert to Video"
4. Download your MP4 file

## Manual Docker Commands

If you prefer not to use docker-compose:

```bash
# Build the image
docker build -t audio-to-video .

# Run the container
docker run -d -p 5000:5000 -v $(pwd)/outputs:/tmp/outputs audio-to-video
```

## Project Structure

```
.
├── app.py                  # Flask application
├── templates/
│   └── index.html         # Web UI
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
└── outputs/              # Generated videos (created on first run)
```

## How It Works

1. User uploads an audio file via the web interface
2. User provides text for the placeholder image
3. Application downloads a 1280x720 image from placehold.co with the specified text
4. FFmpeg combines the audio and image into an MP4 video
5. Video is saved with filename based on the image text
6. User downloads the completed video

## Configuration

### Port

Default port is `5000`. To change it, edit `docker-compose.yml`:

```yaml
ports:
  - "YOUR_PORT:5000"
```

### Max File Size

Default is 100MB. To change it, edit `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## Requirements

- Docker
- Docker Compose (optional, but recommended)

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Check if FFmpeg is installed
```bash
docker exec -it audio-to-video-converter ffmpeg -version
```

### Clear old containers
```bash
docker-compose down
docker-compose up -d --build
```

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5
- **Video Processing**: FFmpeg
- **Image Source**: placehold.co API
- **Video Settings**: 
  - Resolution: 1280x720
  - Video Codec: H.264
  - Audio Codec: AAC (192kbps)
  - Pixel Format: yuv420p (max compatibility)

## License

Open source - use as needed for your projects.
