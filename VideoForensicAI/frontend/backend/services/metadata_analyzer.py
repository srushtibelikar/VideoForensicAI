import json
import os
import subprocess


def run_ffprobe(video_path):
    """
    Extract video/audio metadata using FFprobe.
    """

    ffprobe_path = (
        r"C:\Users\UDDESH\AppData\Local\Microsoft\WinGet\Packages"
        r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
        r"\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
    )

    if not os.path.exists(ffprobe_path):
        print("ERROR: FFprobe executable not found:")
        print(ffprobe_path)
        return None

    if not os.path.exists(video_path):
        print("ERROR: Video file not found:")
        print(video_path)
        return None

    command = [
        ffprobe_path,
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print("FFprobe failed!")
            print("Return code:", result.returncode)
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)
            return None

        if not result.stdout.strip():
            print("FFprobe returned empty output.")
            return None

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        print("FFprobe timed out.")
        return None

    except json.JSONDecodeError as e:
        print("FFprobe JSON parsing error:", e)
        return None

    except Exception as e:
        print("FFprobe error:", e)
        return None


def format_size_mb(file_path):
    """Return file size in MB."""

    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)

    except Exception as e:
        print(f"File size error: {e}")
        return 0


def analyze_metadata(video_path):
    """
    Extract advanced forensic metadata from the video.
    """

    probe = run_ffprobe(video_path)

    filename = os.path.basename(video_path)
    file_size_mb = format_size_mb(video_path)

    metadata = {
        "filename": filename,
        "file_size_mb": file_size_mb,

        "resolution": "Unknown",
        "fps": 0,
        "frame_count": 0,
        "duration_seconds": 0,

        "container": "Unknown",
        "codec": "Unknown",
        "pixel_format": "Unknown",
        "profile": "Unknown",
        "bitrate": "Unknown",
        "creation_time": "Unknown",

        "has_audio": False,
        "audio_codec": None,
        "audio_channels": None,
        "audio_sample_rate": None,

        "metadata_source": "FFprobe unavailable"
    }

    # --------------------------------------------------
    # FFPROBE FAILED
    # --------------------------------------------------

    if not probe:
        metadata["metadata_source"] = "Filesystem only"
        return metadata

    streams = probe.get("streams", [])
    format_info = probe.get("format", {})

    # --------------------------------------------------
    # CONTAINER
    # --------------------------------------------------

    format_name = format_info.get("format_name", "")

    if format_name:

        format_names = format_name.lower().split(",")

        if "mp4" in format_names:
            metadata["container"] = "MP4"

        elif "matroska" in format_names:
            metadata["container"] = "MKV"

        elif "webm" in format_names:
            metadata["container"] = "WEBM"

        elif "avi" in format_names:
            metadata["container"] = "AVI"

        elif "mpegts" in format_names:
            metadata["container"] = "MPEG-TS"

        else:
            metadata["container"] = format_names[0].upper()

    # --------------------------------------------------
    # DURATION
    # --------------------------------------------------

    duration = format_info.get("duration")

    if duration is not None:

        try:
            metadata["duration_seconds"] = round(
                float(duration),
                2
            )

        except (ValueError, TypeError):
            pass

    # --------------------------------------------------
    # BITRATE
    # --------------------------------------------------

    bitrate = format_info.get("bit_rate")

    if bitrate:

        try:
            metadata["bitrate"] = (
                f"{round(int(bitrate) / 1000)} kbps"
            )

        except (ValueError, TypeError):
            metadata["bitrate"] = str(bitrate)

    # --------------------------------------------------
    # CREATION TIME
    # --------------------------------------------------

    tags = format_info.get("tags", {})

    creation_time = (
        tags.get("creation_time")
        or tags.get("com.apple.quicktime.creationdate")
        or tags.get("date")
    )

    if creation_time:
        metadata["creation_time"] = creation_time

    # --------------------------------------------------
    # VIDEO STREAM
    # --------------------------------------------------

    video_stream = next(
        (
            stream
            for stream in streams
            if stream.get("codec_type") == "video"
        ),
        None
    )

    if video_stream:

        # Resolution
        width = video_stream.get("width")
        height = video_stream.get("height")

        if width and height:
            metadata["resolution"] = (
                f"{width}x{height}"
            )

        # Codec
        codec_name = video_stream.get("codec_name")

        if codec_name:
            metadata["codec"] = codec_name.upper()

        # Pixel format
        pixel_format = video_stream.get("pix_fmt")

        if pixel_format:
            metadata["pixel_format"] = pixel_format

        # Profile
        profile = video_stream.get("profile")

        if profile:
            metadata["profile"] = profile

        # FPS
        frame_rate = (
            video_stream.get("avg_frame_rate")
            or video_stream.get("r_frame_rate")
        )

        if frame_rate and frame_rate != "0/0":

            try:

                if "/" in frame_rate:

                    numerator, denominator = (
                        frame_rate.split("/")
                    )

                    if float(denominator) != 0:

                        metadata["fps"] = round(
                            float(numerator)
                            / float(denominator),
                            2
                        )

                else:

                    metadata["fps"] = round(
                        float(frame_rate),
                        2
                    )

            except (
                ValueError,
                ZeroDivisionError
            ):
                pass

        # Frame count
        nb_frames = video_stream.get("nb_frames")

        if nb_frames:

            try:
                metadata["frame_count"] = int(
                    nb_frames
                )

            except (ValueError, TypeError):
                pass

        # Estimate frame count if FFprobe doesn't provide it
        if metadata["frame_count"] == 0:

            if (
                metadata["fps"] > 0
                and metadata["duration_seconds"] > 0
            ):

                metadata["frame_count"] = round(
                    metadata["fps"]
                    * metadata["duration_seconds"]
                )

    # --------------------------------------------------
    # AUDIO STREAM
    # --------------------------------------------------

    audio_stream = next(
        (
            stream
            for stream in streams
            if stream.get("codec_type") == "audio"
        ),
        None
    )

    if audio_stream:

        metadata["has_audio"] = True

        metadata["audio_codec"] = (
            audio_stream.get("codec_name")
            or "Unknown"
        )

        metadata["audio_channels"] = (
            audio_stream.get("channels")
            or 0
        )

        metadata["audio_sample_rate"] = (
            audio_stream.get("sample_rate")
            or "Unknown"
        )

    # --------------------------------------------------
    # SOURCE
    # --------------------------------------------------

    metadata["metadata_source"] = (
        "FFprobe + filesystem"
    )

    return metadata