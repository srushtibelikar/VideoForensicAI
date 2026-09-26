import hashlib
import os

import cv2
import numpy as np


def calculate_frame_difference(frame1, frame2):
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.resize(gray1, (320, 240))
    gray2 = cv2.resize(gray2, (320, 240))
    difference = cv2.absdiff(gray1, gray2)
    return float(np.mean(difference))


def _perceptual_hash(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (32, 32))
    average = small.mean()
    bits = (small >= average).astype(np.uint8).flatten()
    return hashlib.sha256(np.packbits(bits).tobytes()).hexdigest()


def _frame_metrics(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return {
        "brightness": round(float(np.mean(gray)), 2),
        "contrast": round(float(np.std(gray)), 2),
        "blur_score": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2),
        "edge_density": round(float(np.mean(cv2.Canny(gray, 100, 200) > 0)), 4),
    }


def _save_evidence_frame(frame, output_folder, frame_number, reason):
    evidence_folder = os.path.join(output_folder, "evidence")
    os.makedirs(evidence_folder, exist_ok=True)
    filename = f"evidence_{frame_number}_{reason}.jpg"
    path = os.path.join(evidence_folder, filename)
    cv2.imwrite(path, frame)
    return filename


def analyze_frames(video_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Unable to open video")

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25

    frame_number = 0
    sampled_frames = []
    previous_frame = None
    previous_hash = None
    differences = []
    duplicate_frames = 0
    frame_metrics = []
    evidence_frames = []
    suspicious_segments = []
    segment_start = None
    sample_every = max(int(round(fps)), 1)

    while True:
        success, frame = capture.read()
        if not success:
            break

        if frame_number % sample_every == 0:
            frame_name = f"frame_{frame_number}.jpg"
            frame_path = os.path.join(output_folder, frame_name)
            cv2.imwrite(frame_path, frame)

            metrics = _frame_metrics(frame)
            current_hash = _perceptual_hash(frame)
            item = {
                "frame_number": frame_number,
                "timestamp_seconds": round(frame_number / fps, 2),
                "filename": frame_name,
                **metrics,
            }
            sampled_frames.append(item)
            frame_metrics.append(item)

            if previous_frame is not None:
                difference = calculate_frame_difference(previous_frame, frame)
                hash_duplicate = current_hash == previous_hash
                if hash_duplicate or difference < 1.0:
                    duplicate_frames += 1

                change = {
                    "frame_number": frame_number,
                    "timestamp_seconds": round(frame_number / fps, 2),
                    "difference": round(difference, 3),
                    "duplicate": hash_duplicate or difference < 1.0,
                }
                differences.append(change)

                suspicious = difference >= 40 or hash_duplicate
                if suspicious:
                    if segment_start is None:
                        segment_start = frame_number
                    reason = "duplicate" if hash_duplicate else "abrupt_change"
                    evidence_name = _save_evidence_frame(frame, output_folder, frame_number, reason)
                    evidence_frames.append({
                        "frame_number": frame_number,
                        "timestamp_seconds": round(frame_number / fps, 2),
                        "filename": evidence_name,
                        "reason": reason,
                        "difference": round(difference, 3),
                    })
                elif segment_start is not None:
                    suspicious_segments.append({
                        "start_frame": segment_start,
                        "end_frame": frame_number - sample_every,
                        "start_seconds": round(segment_start / fps, 2),
                        "end_seconds": round((frame_number - sample_every) / fps, 2),
                        "reason": "abrupt-change/duplicate indicator",
                    })
                    segment_start = None

                previous_hash = current_hash
            else:
                previous_hash = current_hash

            previous_frame = frame.copy()

        frame_number += 1

    capture.release()

    if segment_start is not None:
        suspicious_segments.append({
            "start_frame": segment_start,
            "end_frame": max(frame_number - sample_every, segment_start),
            "start_seconds": round(segment_start / fps, 2),
            "end_seconds": round(max(frame_number - sample_every, segment_start) / fps, 2),
            "reason": "abrupt-change/duplicate indicator",
        })

    avg_difference = float(np.mean([x["difference"] for x in differences])) if differences else 0
    high_change_frames = [x for x in differences if x["difference"] >= 40]
    low_change_frames = [x for x in differences if x["difference"] < 1]
    blur_frames = [x for x in frame_metrics if x["blur_score"] < 40]

    return {
        "sampled_frames": sampled_frames,
        "sample_count": len(sampled_frames),
        "average_frame_difference": round(avg_difference, 3),
        "duplicate_frame_count": duplicate_frames,
        "high_change_frames": high_change_frames,
        "low_change_frames": low_change_frames,
        "blur_frames": blur_frames,
        "suspicious_segments": suspicious_segments,
        "evidence_frames": evidence_frames,
        "analysis_method": "1 FPS sampling + perceptual hash + pixel difference + blur/edge metrics",
    }
