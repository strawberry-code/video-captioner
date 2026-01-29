#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                            VIDEO CAPTIONER                                     ║
║                                                                                ║
║  Auto-generate subtitles for videos using:                                     ║
║  • Whisper (OpenAI) for speech-to-text transcription                           ║
║  • LanguageTool for grammar correction (optional)                              ║
║                                                                                ║
║  USAGE:                                                                        ║
║    python3 caption_video.py video.mp4                                          ║
║    python3 caption_video.py video.mp4 --soft                                   ║
║    python3 caption_video.py video.mp4 --no-grammar                             ║
║    python3 caption_video.py --check                                            ║
║                                                                                ║
║  OUTPUT:  Files are saved to the "output/" folder                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

WHISPER_MODEL = "medium"  # Options: tiny, base, small, medium, large

# Whisper language code → LanguageTool language code
LANG_MAP = {
    "it": "it", "en": "en-US", "es": "es", "fr": "fr", "de": "de-DE",
    "pt": "pt-PT", "nl": "nl", "pl": "pl-PL", "ru": "ru-RU",
}


# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def check_dependencies():
    """Verify all dependencies are installed."""
    print("\n🔍 Checking dependencies...\n")
    errors = []
    warnings = []

    # 1. FFmpeg (required)
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ FFmpeg installed")
        else:
            errors.append("FFmpeg not found. Install with: brew install ffmpeg")
    except FileNotFoundError:
        errors.append("FFmpeg not found. Install with: brew install ffmpeg")

    # 2. Whisper (required)
    try:
        import whisper
        print("  ✓ Whisper installed")
    except ImportError:
        errors.append("Whisper not installed. Install with: pip install openai-whisper")

    # 3. LanguageTool (optional)
    try:
        import language_tool_python
        lt_path = Path.home() / ".cache" / "language_tool_python"
        if lt_path.exists() and any(lt_path.iterdir()):
            print("  ✓ LanguageTool installed (grammar correction enabled)")
        else:
            print("  ⚠ LanguageTool: local server not downloaded yet")
            print("    → Will download on first use (~255 MB)")
    except ImportError:
        warnings.append(
            "LanguageTool not installed (grammar correction disabled)\n"
            "    → To install: pip install language_tool_python"
        )

    # Show errors
    if errors:
        print("\n❌ ERROR - Required dependencies missing:\n")
        for err in errors:
            print(f"  • {err}")
        print()
        sys.exit(1)

    # Show warnings
    if warnings:
        print()
        for warn in warnings:
            print(f"  ⚠ {warn}")

    print("\n" + "─" * 70 + "\n")
    return len(warnings) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def extract_audio(video_path: Path, audio_path: Path) -> None:
    """Extract audio from video."""
    print("📢 Extracting audio...")
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"   → {audio_path.name}")


def transcribe_audio(audio_path: Path) -> dict:
    """Transcribe audio using Whisper."""
    import whisper

    print(f"🎙️  Transcribing with Whisper ({WHISPER_MODEL})...")
    print("   (this may take a few minutes)")

    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(str(audio_path), language=None, verbose=False)

    lang = result.get("language", "??")
    segments = len(result["segments"])
    print(f"   → Language: {lang} | Segments: {segments}")

    return result


def correct_grammar(segments: list, lang_code: str) -> list:
    """Fix grammar errors using LanguageTool."""
    try:
        import language_tool_python
    except ImportError:
        return segments

    lt_lang = LANG_MAP.get(lang_code, "en-US")
    print(f"✏️  Correcting grammar ({lt_lang})...")

    try:
        tool = language_tool_python.LanguageTool(lt_lang)
    except Exception as e:
        print(f"   ⚠ LanguageTool unavailable: {e}")
        return segments

    corrected = []
    fixes = 0

    for seg in segments:
        original = seg["text"].strip()
        fixed = tool.correct(original)
        if fixed != original:
            fixes += 1
        corrected.append({"start": seg["start"], "end": seg["end"], "text": fixed})

    tool.close()
    print(f"   → {fixes} corrections applied")

    return corrected


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_srt(segments: list, srt_path: Path) -> None:
    """Save subtitles in SRT format."""
    print("💾 Saving SRT subtitles...")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            f.write(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n\n")
    print(f"   → {srt_path.name}")


def save_transcript(segments: list, txt_path: Path) -> None:
    """Save full transcript as plain text."""
    print("💾 Saving transcript...")
    text = " ".join(seg["text"].strip() for seg in segments)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"   → {txt_path.name}")


def burn_subtitles(video_path: Path, srt_path: Path, output_path: Path) -> None:
    """Burn subtitles into video (always visible)."""
    print("🎬 Creating video with burned-in subtitles...")
    print("   (this may take a few minutes)")

    srt_escaped = str(srt_path).replace(":", "\\:").replace("'", "\\'")
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", f"subtitles='{srt_escaped}'",
        "-c:a", "copy", str(output_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"   → {output_path.name}")


def embed_subtitles(video_path: Path, srt_path: Path, output_path: Path) -> None:
    """Embed subtitles as a separate track (toggleable in player)."""
    print("🎬 Creating video with soft subtitles...")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path), "-i", str(srt_path),
        "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
        str(output_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"   → {output_path.name}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate subtitles for videos",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "video", nargs="?", type=Path,
        help="Video file to process (e.g., video.mp4)"
    )
    parser.add_argument(
        "--soft", action="store_true",
        help="Embed subtitles as separate track (toggleable in player)"
    )
    parser.add_argument(
        "--no-grammar", action="store_true",
        help="Disable grammar correction"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Only check dependencies"
    )
    args = parser.parse_args()

    # Header
    print(__doc__)

    # Check dependencies
    has_grammar = check_dependencies()

    if args.check:
        print("✅ Check complete.\n")
        sys.exit(0)

    # Validate video file
    if not args.video:
        print("❌ Error: please specify a video file\n")
        print("   Usage: python3 caption_video.py video.mp4\n")
        sys.exit(1)

    if not args.video.exists():
        print(f"❌ Error: file not found: {args.video}\n")
        sys.exit(1)

    video_path = args.video.resolve()
    name = video_path.stem

    # Output folder
    output = Path(__file__).parent / "output"
    output.mkdir(exist_ok=True)

    print(f"📁 Video: {video_path.name}\n")
    print("─" * 70 + "\n")

    # Output paths
    audio_path = output / f"{name}_temp.wav"
    srt_path = output / f"{name}.srt"
    txt_path = output / f"{name}_transcript.txt"
    suffix = "_soft" if args.soft else ""
    video_out = output / f"{name}_captioned{suffix}.mp4"

    # Pipeline
    extract_audio(video_path, audio_path)
    result = transcribe_audio(audio_path)
    segments = result["segments"]
    lang = result.get("language", "en")

    if has_grammar and not args.no_grammar:
        segments = correct_grammar(segments, lang)

    save_srt(segments, srt_path)
    save_transcript(segments, txt_path)

    if args.soft:
        embed_subtitles(video_path, srt_path, video_out)
    else:
        burn_subtitles(video_path, srt_path, video_out)

    # Cleanup
    audio_path.unlink()

    # Summary
    print("\n" + "═" * 70)
    print("✅ DONE!")
    print("═" * 70)
    print(f"\n📂 Output files:\n")
    print(f"   • {video_out.name:<40} (video)")
    print(f"   • {srt_path.name:<40} (subtitles)")
    print(f"   • {txt_path.name:<40} (transcript)")
    print()


if __name__ == "__main__":
    main()
