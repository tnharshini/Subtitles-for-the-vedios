import os
from flask import Flask, render_template, request, redirect
import moviepy.editor as mp
from speech_recognition import Recognizer, AudioFile

app = Flask(__name__)

# Folder to store uploaded videos
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Function to extract audio and convert it to text
def video_to_audio_text(video_path):
    recognizer = Recognizer()

    # Extract audio from video
    video = mp.VideoFileClip(video_path)
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    video.close()  # Ensure video file is closed after extracting audio

    # Convert audio to text
    with AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
    
    # Clean up the audio file after processing
    os.remove(audio_path)
    
    return text

# Route to handle video upload
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return redirect(request.url)
    
    video = request.files['video']
    
    if video.filename == '':
        return redirect(request.url)
    
    if video:
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)
        
        try:
            # Generate subtitles from video
            text = video_to_audio_text(video_path)
        finally:
            # Clean up the uploaded video file
            os.remove(video_path)  # Ensure video is deleted after processing
        
        return render_template('result.html', text=text)

if __name__ == '__main__':
    app.run(debug=True)
