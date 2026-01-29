# Video Captioner

Auto-generate subtitles for any video using AI transcription and grammar correction.

## Features

- **Speech-to-text** with OpenAI Whisper (auto-detects language)
- **Grammar correction** with LanguageTool (optional, 30+ languages)
- **Burned-in** or **soft** subtitles
- Outputs: captioned video, SRT file, plain text transcript

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
python3 caption_video.py video.mp4                 # Burned-in subtitles
python3 caption_video.py video.mp4 --soft          # Soft subtitles (toggleable)
python3 caption_video.py video.mp4 --no-grammar    # Skip grammar correction
python3 caption_video.py --check                   # Check dependencies
```

## Output

Files are saved to `output/`:

```
output/
├── video_captioned.mp4    # Video with subtitles
├── video.srt              # Subtitle file
└── video_transcript.txt   # Plain text transcript
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
