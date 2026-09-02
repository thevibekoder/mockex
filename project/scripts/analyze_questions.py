"""
analyze_questions.py
---------------------
Reads transcript_<id>.json (from extract_transcript.py) and asks a Groq-hosted
model to split it into quiz questions, each with a start timestamp (seconds)
and a short title/summary.

Install:
    pip install groq --break-system-packages

Set your API key:
    export GROQ_API_KEY=gsk_...

Usage:
    python analyze_questions.py transcript_XXXXXXXXXXX.json
"""

import argparse
import json
import os
import sys
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are analyzing the transcript of an exam-prep / quiz-review video.
The teacher goes through quiz questions one by one, discussing the solution to each.

Your job: identify each NEW question the teacher starts discussing, in order,
and return the timestamp (in seconds) where the discussion of that question begins.

Rules:
- Only mark the moment a NEW question starts (not sub-steps within the same question).
- Ignore intros, banter, or wrap-up commentary - only number actual quiz questions.
- Give each question a short (<12 word) topic label, in English, summarizing what it's about.
- Output ONLY valid JSON, no markdown fences, no commentary. Format:

{
  "questions": [
    {"number": 1, "start_seconds": 351, "label": "Income split between essentials and rent"},
    {"number": 2, "start_seconds": 448, "label": "Mixing two varieties of sugar, no profit/loss"}
  ]
}
"""


def seconds_from_segments(segments):
    """Builds a single text blob with inline [t=SECONDS] markers so the model
    can cite exact timestamps."""
    lines = []
    for seg in segments:
        lines.append(f"[t={seg['start']}] {seg['text']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_json", help="Path to transcript_<id>.json")
    parser.add_argument("--out", default=None, help="Output JSON path")
    args = parser.parse_args()

    with open(args.transcript_json, encoding="utf-8") as f:
        data = json.load(f)

    video_id = data["video_id"]
    blob = seconds_from_segments(data["segments"])

    client = Groq()  # reads GROQ_API_KEY from env

    # For long videos, you may need to chunk `blob` and merge results.
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": blob},
        ],
        response_format={"type": "json_object"},
    )

    text = resp.choices[0].message.content
    text = text.strip().strip("`")
    if text.startswith("json"):
        text = text[4:].strip()

    result = json.loads(text)
    result["video_id"] = video_id

    out_path = args.out or f"questions_{video_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Found {len(result['questions'])} questions -> {out_path}")


if __name__ == "__main__":
    main()
