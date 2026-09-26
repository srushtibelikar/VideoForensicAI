from services.audio_analyzer import analyze_audio
from services.frame_analyzer import analyze_frames
from services.hash_service import calculate_sha256
from services.metadata_analyzer import analyze_metadata


def analyze_video(video_path, frame_folder):
    metadata = analyze_metadata(video_path)
    file_hash = calculate_sha256(video_path)
    frame_analysis = analyze_frames(video_path, frame_folder)
    audio_analysis = analyze_audio(video_path)

    tampering = detect_tampering_indicators(metadata, frame_analysis, audio_analysis)
    risk_score = calculate_risk_score(metadata, frame_analysis, tampering)
    classification = classify_video(risk_score)

    return {
        "metadata": metadata,
        "sha256": file_hash,
        "frame_analysis": frame_analysis,
        "audio_analysis": audio_analysis,
        "tampering_detection": tampering,
        "risk_score": risk_score,
        "classification": classification,
    }


def detect_tampering_indicators(metadata, frame_analysis, audio_analysis):
    indicators = []
    if frame_analysis["duplicate_frame_count"] > 0:
        indicators.append({
            "type": "repeated-frame",
            "severity": "medium",
            "message": f"{frame_analysis['duplicate_frame_count']} sampled frame transition(s) appear repeated or near-identical.",
        })
    if frame_analysis["high_change_frames"]:
        indicators.append({
            "type": "abrupt-change",
            "severity": "medium",
            "message": f"{len(frame_analysis['high_change_frames'])} sampled transition(s) have unusually high pixel difference.",
        })
    if frame_analysis["blur_frames"]:
        indicators.append({
            "type": "blur/anomaly",
            "severity": "low",
            "message": f"{len(frame_analysis['blur_frames'])} sampled frames have low Laplacian variance (possible blur or focus change).",
        })
    if metadata.get("creation_time") == "Not available":
        indicators.append({
            "type": "metadata-gap",
            "severity": "info",
            "message": "Container creation-time metadata was not available.",
        })
    if not metadata.get("has_audio"):
        indicators.append({
            "type": "audio",
            "severity": "info",
            "message": "No audio stream was detected; audio continuity cannot be assessed.",
        })

    return {
        "status": "Indicators detected" if indicators else "No automated indicators detected",
        "indicator_count": len(indicators),
        "indicators": indicators,
        "disclaimer": "These are automated forensic indicators, not proof of manipulation.",
    }


def calculate_risk_score(metadata, frame_analysis, tampering):
    score = 0
    sampled_count = frame_analysis["sample_count"]
    duplicate_ratio = (
        frame_analysis["duplicate_frame_count"] / max(sampled_count, 1)
    )
    high_change_count = len(frame_analysis["high_change_frames"])

    if duplicate_ratio > 0.10:
        score += 30
    elif duplicate_ratio > 0.03:
        score += 15
    if high_change_count > 10:
        score += 30
    elif high_change_count > 5:
        score += 20
    elif high_change_count > 0:
        score += 10
    if len(frame_analysis["suspicious_segments"]) > 3:
        score += 15
    if metadata["frame_count"] < 10:
        score += 10
    if metadata["fps"] <= 0:
        score += 10

    return min(score, 100)


def classify_video(score):
    if score >= 70:
        return "HIGH RISK"
    if score >= 40:
        return "SUSPICIOUS"
    return "LOW RISK"
