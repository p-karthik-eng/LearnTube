import re
import sys
import json
import subprocess
import tempfile
import os

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be/([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL")

def get_transcript_youtube_api(video_id, lang='en'):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Try to fetch the English transcript (official or auto-generated)
        try:
            transcript = transcript_list.find_transcript([lang])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript([lang])
        entries = transcript.fetch()
        return {
            "source": "youtube_transcript_api",
            "language": transcript.language_code,
            "is_generated": transcript.is_generated,
            "text": " ".join([entry['text'] for entry in entries])
            # Removed transcript field to reduce data size
        }
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"youtube_transcript_api error: {e}", file=sys.stderr)
        return None

def get_transcript_ytdlp(video_id, lang='en'):
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            r"C:\\Users\\karth\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\yt-dlp.exe",
            f"https://www.youtube.com/watch?v={video_id}",
            "--write-auto-subs",
            "--sub-lang", lang,
            "--skip-download",
            "--sub-format", "json3",
            "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            for fname in os.listdir(tmpdir):
                if fname.endswith(".json3"):
                    with open(os.path.join(tmpdir, fname), encoding="utf-8") as f:
                        data = json.load(f)
                    events = data.get("events", [])
                    lines = []
                    for event in events:
                        if "segs" in event:
                            lines.extend(seg["utf8"] for seg in event["segs"] if "utf8" in seg)
                    return {
                        "source": "yt-dlp",
                        "language": lang,
                        "is_generated": True,
                        "text": " ".join(lines)
                        # Removed transcript field to reduce data size
                    }
        except subprocess.CalledProcessError as e:
            print(f"yt-dlp error: {e}", file=sys.stderr)
            return None
    return None

def transcribe_whisper(video_id, lang='en'):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        cmd = [
            r"C:\\Users\\karth\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\yt-dlp.exe",
            f"https://www.youtube.com/watch?v={video_id}",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", audio_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            with open(audio_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return {
                "source": "whisper",
                "language": lang,
                "is_generated": True,
                "text": transcript["text"]
                # Removed transcript field to reduce data size
            }
        except Exception as e:
            print(f"Whisper error: {e}", file=sys.stderr)
            return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_youtube_transcript.py <youtube_url>")
        sys.exit(1)
    url = sys.argv[1]
    video_id = extract_video_id(url)

    # 1. Try youtube_transcript_api (official and auto-generated)
    result = get_transcript_youtube_api(video_id)
    if result and result.get("text"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 2. Fallback: yt-dlp auto-generated captions
    result = get_transcript_ytdlp(video_id)
    if result and result.get("text"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 3. Fallback: Whisper transcription
    result = transcribe_whisper(video_id)
    if result and result.get("text"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(json.dumps({
        "error": "No captions accessible for this video (official, auto-generated, or Whisper)."
    }))

if __name__ == "__main__":
    main() 