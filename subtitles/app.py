import os
from flask import Flask, render_template, request, redirect
import moviepy.editor as mp
from speech_recognition import Recognizer, AudioFile
import math

app = Flask(__name__)

# Folder to store uploaded videos
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Function to process video and convert it to audio chunks, then transcribe each chunk
def video_to_audio_text(video_path):
    recognizer = Recognizer()

    # Extract audio from video
    video = mp.VideoFileClip(video_path)
    duration = video.duration  # Get video duration in seconds

    # Define chunk size (in seconds) to break video into smaller pieces, e.g., 10 seconds per chunk
    chunk_size = 10
    overlap = 1  # Define 1 second overlap between chunks
    num_chunks = math.ceil(duration / chunk_size)

    transcript = ""
    
    for i in range(num_chunks):
        start_time = max(i * chunk_size - overlap, 0)  # Ensure start_time is not negative
        end_time = min((i + 1) * chunk_size, duration)

        # Extract a segment of the video (from start_time to end_time)
        video_chunk = video.subclip(start_time, end_time)
        audio_chunk_path = f"audio_chunk_{i}.wav"
        video_chunk.audio.write_audiofile(audio_chunk_path)

        # Process the audio chunk
        with AudioFile(audio_chunk_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                transcript += text + " "
                print(f"Processed chunk {i}: {text}")
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
        
        # Clean up the audio chunk file
        os.remove(audio_chunk_path)

    video.close()  # Close the video file after processing
    
    return transcript

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
