import wave, math, contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip

# ref: https://towardsdatascience.com/transcribing-interview-data-from-video-to-text-with-python-5cdb6689eea1

transcribed_audio_file_name = "transcribed_speech.wav"
zoom_video_file_name = "Advanced Security - Intro to Hardware, Day 2.mp4"

audioclip = AudioFileClip(zoom_video_file_name)
audioclip.write_audiofile(transcribed_audio_file_name)

with contextlib.closing(wave.open(transcribed_audio_file_name,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
total_duration = math.ceil(duration / 60)
r = sr.Recognizer()
for i in range(0, total_duration):
    with sr.AudioFile(transcribed_audio_file_name) as source:
        audio = r.record(source, offset=i*60, duration=60)
    f = open("transcription.txt", "a")
    f.write(r.recognize_google(audio))
    f.write(" ")
f.close()
