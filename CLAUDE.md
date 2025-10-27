# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Flask-based web application that converts audio files to MP4 videos with custom placeholder images. The application runs in Docker and uses FFmpeg for video processing.

## Development Commands

### Docker Development

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs

# Stop the application
docker-compose down

# Rebuild after changes
docker-compose down
docker-compose up -d --build

# Access the running container
docker exec -it audio-to-video-converter bash
```

### Manual Docker Commands

```bash
# Build the Docker image
docker build -t audio-to-video .

# Run container with volume mount
docker run -d -p 5000:5000 -v $(pwd)/outputs:/tmp/outputs audio-to-video
```

### Testing FFmpeg

```bash
# Verify FFmpeg is installed in container
docker exec -it audio-to-video-converter ffmpeg -version
```

## Architecture

### Application Flow

1. **Upload Phase**: User uploads audio file via web UI (index.html)
2. **Image Generation**: Application fetches placeholder image from placehold.co API with custom text
3. **Video Processing**: FFmpeg combines static image with audio track
4. **Download Phase**: User downloads generated MP4 file

### Key Components

- **app.py**: Flask backend with three routes:
  - `/` - Serves the web UI
  - `/convert` - POST endpoint that handles audio upload, downloads placeholder image, and invokes FFmpeg
  - `/download/<filename>` - Serves generated MP4 files

- **templates/index.html**: Single-page web UI with Bootstrap 5, handles file upload and displays conversion progress

- **FFmpeg Processing** (app.py:64-77): Combines audio and image using these key parameters:
  - `-loop 1`: Loops the static image
  - `-tune stillimage`: Optimizes for static image encoding
  - `-c:a aac -b:a 192k`: AAC audio codec at 192kbps
  - `-pix_fmt yuv420p`: Ensures maximum player compatibility
  - `-shortest`: Ends video when audio ends

### File System Layout

- `/tmp/uploads/`: Temporary storage for uploaded audio and downloaded images (cleaned after conversion)
- `/tmp/outputs/`: Persistent storage for generated MP4 files (mounted as volume in docker-compose.yml)
- Output filename is generated from user's image text with spaces replaced by underscores

### Configuration Points

- **Max file size**: app.py:10 - Currently 100MB
- **Supported audio formats**: app.py:18 - mp3, wav, ogg, m4a, flac, aac
- **Video resolution**: app.py:53 - 1280x720 (HD)
- **Brand color**: app.py:53 - Cabernet (#670038)
- **Port**: docker-compose.yml:8 - 5000

### External Dependencies

- **placehold.co API**: Used for generating placeholder images with custom text (app.py:53)
- Format: `https://placehold.co/1280x720/670038/ffffff?text={user_text}`
- No API key required

## Important Notes

- The Flask app runs in production mode (debug=False) inside Docker
- Temporary files (uploaded audio and downloaded images) are deleted after successful conversion (app.py:85-86)
- The index.html file must be in the templates/ directory for Flask's render_template() to work
- FFmpeg errors are captured and returned to user via JSON response (app.py:82)
