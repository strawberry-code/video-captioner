# Media Captioner

Auto-generate subtitles for videos and transcriptions for audio using AI transcription and grammar correction.

## Features

- **Speech-to-text** with OpenAI Whisper (auto-detects language)
- **Grammar correction** with LanguageTool (optional, 30+ languages)
- **Burned-in** or **soft** subtitles (video only)
- Supports video and audio files
- Outputs: captioned video, SRT file, plain text transcript

## Supported Formats

| Type  | Extensions                                    |
|-------|-----------------------------------------------|
| Video | mp4, mkv, mov, avi, webm, flv, wmv, m4v       |
| Audio | mp3, wav, flac, aac, ogg, m4a, wma, opus      |

## Installation

```bash
# Required
brew install ffmpeg
pip install openai-whisper

# Optional (grammar correction)
pip install language_tool_python
```

## Usage

```bash
# Video
python3 caption_video.py video.mp4                 # Burned-in subtitles
python3 caption_video.py video.mp4 --soft          # Soft subtitles (toggleable)
python3 caption_video.py video.mp4 --no-grammar    # Skip grammar correction

# Audio
python3 caption_video.py podcast.mp3               # Transcribe audio file
python3 caption_video.py recording.wav             # Any supported audio format

# Check dependencies
python3 caption_video.py --check
```

## Output

Files are saved to `output/`:

**Video input:**
```
output/
├── video_captioned.mp4    # Video with subtitles
├── video.srt              # Subtitle file
└── video_transcript.txt   # Plain text transcript
```

**Audio input:**
```
output/
├── audio.srt              # Subtitle file (with timestamps)
└── audio_transcript.txt   # Plain text transcript
```

## Configuration

Edit `WHISPER_MODEL` in the script to change transcription quality/speed:

| Model  | Speed  | Accuracy |
|--------|--------|----------|
| tiny   | Fast   | Lower    |
| base   | Fast   | Good     |
| small  | Medium | Better   |
| medium | Slow   | High     |
| large  | Slower | Highest  |

## License

MIT
