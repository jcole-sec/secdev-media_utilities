Install ffmpeg
```
sudo apt install ffmpeg
```

Audio extract from video file:
```
ffmpeg -i input_video.mp4 -q:a 0 -map a output_audio.wav
```
