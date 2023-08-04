from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import os
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)





# def process_video(video_path):
#     clip = VideoFileClip(video_path)
#     total_frames = int(clip.fps * clip.duration)
    
#     for i, frame in enumerate(clip.iter_frames()):
#         # Process each frame here
#         # ...

#         # Calculate the progress and send it to the frontend
#         progress_percentage = (i + 1) / total_frames * 100
#         socketio.emit('progress', {'progress_percentage': progress_percentage})

#     # After processing is complete, save the processed video to 'uploads/output.mp4'
#     output_path = os.path.join('uploads', 'output.mp4')
#     clip.write_videofile(output_path, codec='libx264')

#     # Notify the frontend that processing is completed
#     socketio.emit('processing_complete')    



def process_video(video_path):
    clip = VideoFileClip(video_path)
    total_frames = int(clip.fps * clip.duration)

    def custom_callback(progress):
        # Calculate the progress based on the percentage of video frames processed
        progress_percentage = progress * 100
        socketio.emit('progress', {'progress_percentage': progress_percentage})

    # Write the video file with the custom callback
    output_path = os.path.join('uploads', 'output.mp4')
    clip.write_videofile(output_path, codec='libx264', callback=custom_callback)
    clip.close()
    # Notify the frontend that processing is completed
    socketio.emit('processing_complete')




@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        video = request.files['video']
        video_path = os.path.join('uploads', video.filename)
        video.save(video_path)
        socketio.start_background_task(target=process_video, video_path=video_path)
        return redirect(url_for('progress'))
    return render_template('upload.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

if __name__ == '__main__':
    socketio.run(app)

