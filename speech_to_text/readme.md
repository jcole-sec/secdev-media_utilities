Install ffmpeg
```
sudo apt install ffmpeg
```

Audio extract from video file:
```
ffmpeg -i input_video.mp4 -q:a 0 -map a output_audio.wav
```
Alt.

```
ffmpeg -i input_video.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le output_audio.wav
```


Transcribe audio to text
```
pip install faster-whisper
# Base-size model is a good start; use medium/large on GPU for best accuracy
python - <<'PY'
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cuda", compute_type="float16")  # or cpu / int8
segments, info = model.transcribe("output_audio.wav", vad_filter=True)
with open("transcript.srt","w",encoding="utf-8") as srt, open("transcript.txt","w",encoding="utf-8") as txt:
    i=1
    for seg in segments:
        start = seg.start; end = seg.end; text = seg.text.strip()
        # write SRT
        srt.write(f"{i}\n")
        to_ts=lambda t:f"{int(t//3600):02}:{int((t%3600)//60):02}:{int(t%60):02},{int((t%1)*1000):03}"
        srt.write(f"{to_ts(start)} --> {to_ts(end)}\n{text}\n\n"); i+=1
        txt.write(text+" ")
PY
```

