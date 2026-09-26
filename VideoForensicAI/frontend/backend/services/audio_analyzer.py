import json
import shutil
import subprocess


def analyze_audio(video_path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {
            "available": False,
            "status": "ffprobe not installed; audio analysis unavailable",
            "streams": [],
        }

    command = [
        ffprobe, "-v", "error", "-select_streams", "a",
        "-show_entries",
        "stream=index,codec_name,codec_long_name,sample_rate,channels,channel_layout,duration,bit_rate:stream_tags=language,title",
        "-of", "json", video_path,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if completed.returncode != 0:
            return {"available": False, "status": "ffprobe audio inspection failed", "streams": []}
        payload = json.loads(completed.stdout or "{}")
        streams = payload.get("streams", [])
        return {
            "available": True,
            "status": "Audio stream detected" if streams else "No audio stream detected",
            "stream_count": len(streams),
            "streams": streams,
        }
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"available": False, "status": f"Audio analysis failed: {exc}", "streams": []}
