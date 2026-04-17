#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from faster_whisper import WhisperModel

MODEL_NAME = "tiny"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: transcribe_audio.py <audio-file>", file=sys.stderr)
        return 2
    audio = Path(sys.argv[1])
    if not audio.exists():
        print(f"file not found: {audio}", file=sys.stderr)
        return 2

    model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio), vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    print(json.dumps({
        "model": MODEL_NAME,
        "language": info.language,
        "duration": info.duration,
        "text": text,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
