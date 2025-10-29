from flask import Flask, render_template, request, send_file, jsonify
import os
import requests
from werkzeug.utils import secure_filename
import subprocess
from pathlib import Path
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 350 * 1024 * 1024  # 350MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['OUTPUT_FOLDER'] = '/tmp/outputs'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_audio_to_video():
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        image_text = request.form.get('image_text', 'Video')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        if not allowed_file(audio_file.filename):
            return jsonify({'error': 'Invalid audio file format'}), 400
        
        # Save audio file
        audio_filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        audio_file.save(audio_path)
        
        # Generate output filename from image text
        output_filename = image_text.replace(' ', '_') + '.mp4'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Download placeholder image (1280x720 is a good video resolution)
        image_url = f'https://placehold.co/1280x720/670038/ffffff?text={image_text}'
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.png')
        
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
        else:
            return jsonify({'error': 'Failed to download placeholder image'}), 500
        
        # Convert audio + image to video using FFmpeg
        cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'error': f'FFmpeg error: {result.stderr}'}), 500
        
        # Clean up temporary files
        os.remove(audio_path)
        os.remove(image_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'message': 'Video created successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
