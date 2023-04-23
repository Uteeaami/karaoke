# Karaoke

This is a karaoke app that separates the vocals from a song and displays lyrics in sync with the music.

## Prerequisites

- Python: 3.10

## Getting started

Clone the repository:
- git clone https://github.com/<username>/karaoke.git

Install required packages from requirements.txt:
- pip install -r requirements.txt

Due to some collisions with Spleeter and Flask, please install the following versions of Spleeter, Click and Typer packages:
- pip install spleeter
- pip install click==8.0.4
- pip install typer==0.6.1

Download the whisper model from:

- https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-large-v1.bin (rename large.bin)
- https://github.com/ggerganov/whisper.cpp/releases/download/v1.2.1/whisper-bin-x64.zip

Unzip the files to `karaoke/executables/whisper`.

## Credits

This app uses the following open source software:

- [Spleeter](https://github.com/deezer/spleeter)
- [Flask](https://flask.palletsprojects.com/en/2.1.x/)
- [Whisper](https://github.com/ggerganov/whisper.cpp)
