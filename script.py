from flask import Flask, request, send_file
from flask.helpers import send_from_directory
from flask_cors import CORS
import json
import subprocess
from yt_dlp import YoutubeDL
import os


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

root = os.getcwd()
execs = root + "\executables"
songs = root + "\song_files"
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
    
    audio_file = os.path.join(songs, title, "audio.wav")
    video_file = os.path.join(songs, title, filename)

    cmd = [
        execs + "/ffmpeg.exe",
        "-y",
        "-i",
        video_file,
        "-map",
        "0:a",
        "-y",
        audio_file,
    ]

    subprocess.call(cmd)

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

    # WHISPER
    # process sample rate to 16k for whisper input
    command = (execs + "/ffmpeg.exe -y -i " + whisper + "/vocals.wav -ar 16000 "
               + whisper + "/vocals16k.wav")
    print(command)
    subprocess.call(command, shell=True)

    os.chdir(whisper)

    command = ("main.exe -m large.bin -f vocals16k.wav -ml 1 -l fi -t 6 -osrt --prompt lyrics.txt")
    subprocess.call(command, shell=True)
   

    command = ["py", "karaoke_algo.py"]
    subprocess.call(command)

    print(command)

    print(f'"{title.title()}"')
    os.chdir(songs)
    os.chdir(title)
    print("DIRECTORY: ", os.getcwd())

    filename = f'"{filename}"'
    command = ("ffmpeg -y -i " + filename + " -vf subtitles=../../executables/whisper/subs.srt -c:a copy " + "out.webm")
    print(command)
    subprocess.call(command, shell=True)
    command = ("del " + filename)
    subprocess.call(command, shell=True)
    command = ("move out.webm " + filename)
    subprocess.call(command, shell=True)
    print(command)

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