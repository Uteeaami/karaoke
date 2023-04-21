from flask import Flask, request, send_file
from flask.helpers import send_from_directory
from flask_cors import CORS
import ffmpeg
import json
import subprocess
from yt_dlp import YoutubeDL
import os


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

root = os.getcwd()
execs = root + "\executables"
songs = root + "\karaoke"
whisper = execs + "\whisper"

#Download and separation of audio
@app.route("/script", methods=["GET", "POST"])
def script():
    language = request.args.get('lang')
    url = request.args.get('url')
    os.chdir(root)
    URLS = [url]
    with YoutubeDL() as ydl:
        info = ydl.extract_info(URLS[0], download=False)
        title = info["title"]
        identifier = info["id"]
        filename = title + " [" + identifier + "]"
        filename = f'{filename.title()}.webm'
        cmd_str = f'{title.title()}'
        os.chdir(songs)
        if not os.path.exists(cmd_str):
            os.mkdir(cmd_str)
            print(f"Directory {cmd_str} created")
        else:
            print(f"Directory {cmd_str} already exists")
        os.chdir(songs + "\\" + title)
        ydl.download(URLS)

    audio_file = os.path.join(songs,title, "audio.wav")
    video_file = os.path.join(songs, title, filename)

    (
        ffmpeg
        .input(video_file)
        .audio
        .output(audio_file, format="wav", acodec="pcm_s16le", ar="48000", ac="2")
        .overwrite_output()
        .run()
    )

    #Spleeter separates lyrics from vocals
    from spleeter.separator import Separator
    from spleeter.audio.adapter import AudioAdapter
    default_adapter = AudioAdapter.default()

    separator = Separator('spleeter:2stems')
    waveform, sample_rate = default_adapter.load('./audio.wav')
    prediction = separator.separate(waveform)

    for name, component in prediction.items():
        save_path = os.path.join(execs + '\\whisper', f'{name}.wav')
        default_adapter.save(save_path, component, sample_rate)

    lyrics = request.json['lyrics']
    with open(os.path.join(execs, 'whisper', 'lyrics.txt'), 'w', encoding='utf-8') as f:
        f.write(lyrics)

    return title + "|" + "Done"

#Route to video
@app.route('/video/<song_name>')
def serve_video(song_name):
    video_folder = os.path.join(songs, song_name)
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".webm")]
    if len(video_files) == 0:
        return "Video not found"
    return send_file(os.path.join(video_folder, video_files[0]), mimetype='video/webm')

#Route to all videos
@app.route('/video')
def serve_name():
    song_names = []
    for file_name in os.listdir(songs):
        song_names.append(file_name)
    return json.dumps({"song_names": song_names})

#Backend defined to use production build
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run()