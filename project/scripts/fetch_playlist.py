"""
fetch_playlist.py
------------------
Lists every video ID + title in a YouTube playlist, in order.

Install:
    pip install yt-dlp --break-system-packages

Usage:
    python fetch_playlist.py <playlist_url_or_id> --out playlist.json
"""

import argparse
import json
import subprocess
import sys


def fetch_playlist_entries(playlist_url: str):
    """Uses yt-dlp in flat-playlist mode: fast, no video downloads, just metadata."""
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        playlist_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("yt-dlp error:", result.stderr, file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    entries = []
    for e in data.get("entries", []):
        if not e:
            continue
        entries.append({
            "video_id": e.get("id"),
            "title": e.get("title"),
        })
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist", help="Playlist URL or ID")
    parser.add_argument("--out", default="playlist.json")
    args = parser.parse_args()

    entries = fetch_playlist_entries(args.playlist)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"videos": entries}, f, ensure_ascii=False, indent=2)

    print(f"Found {len(entries)} videos -> {args.out}")


if __name__ == "__main__":
    main()
