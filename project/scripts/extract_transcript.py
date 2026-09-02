"""
extract_transcript.py
----------------------
Pulls the timestamped transcript for a YouTube video and saves it as JSON.

Install:
    pip install youtube-transcript-api --break-system-packages

Usage:
    python extract_transcript.py <video_id_or_url> [--lang hi]

Output:
    transcript_<video_id>.json  ->  [{"start": 1.2, "duration": 3.4, "text": "..."}]
"""

import argparse
import json
import re
import sys
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url_or_id: str) -> str:
    """Accepts a raw video ID or any common YouTube URL format."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    # assume it's already a bare ID
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
        return url_or_id
    raise ValueError(f"Could not parse video ID from: {url_or_id}")


def fetch_transcript(video_id: str, languages=("hi", "en")):
    api = YouTubeTranscriptApi()
    # Tries requested languages in order, falls back to auto-generated if needed
    transcript_list = api.list(video_id)
    try:
        transcript = transcript_list.find_transcript(languages)
    except Exception:
        transcript = transcript_list.find_generated_transcript(languages)
    return transcript.fetch()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="YouTube video URL or ID")
    parser.add_argument("--lang", nargs="+", default=["hi", "en"],
                         help="Preferred language codes, in priority order")
    parser.add_argument("--out", default=None, help="Output JSON path")
    args = parser.parse_args()

    video_id = get_video_id(args.video)
    print(f"Fetching transcript for video: {video_id}")

    raw = fetch_transcript(video_id, tuple(args.lang))
    segments = [
        {"start": round(seg.start, 2), "duration": round(seg.duration, 2), "text": seg.text}
        for seg in raw
    ]

    out_path = args.out or f"transcript_{video_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"video_id": video_id, "segments": segments}, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(segments)} segments -> {out_path}")


if __name__ == "__main__":
    main()
