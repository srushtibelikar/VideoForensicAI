import os
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS
from utils.file_utils import generate_unique_filename, allowed_file
from services.video_analyzer import analyze_video
from services.metadata_analyzer import analyze_metadata
from services.report_generator import generate_report

forensic_bp = Blueprint("forensic", __name__)


@forensic_bp.route("/analyze", methods=["POST"])
def analyze():

    # ---------------------------------------------------------
    # 1. Check uploaded video
    # ---------------------------------------------------------
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files["video"]

    if video.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(video.filename, ALLOWED_EXTENSIONS):
        return jsonify({"error": "Unsupported video format"}), 400

    # ---------------------------------------------------------
    # 2. Save uploaded video
    # ---------------------------------------------------------
    filename = secure_filename(video.filename)
    unique_filename = generate_unique_filename(filename)

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    video.save(upload_path)

    # ---------------------------------------------------------
    # 3. Create frame folder
    # ---------------------------------------------------------
    frame_folder = os.path.join(
        current_app.config["FRAME_FOLDER"],
        os.path.splitext(unique_filename)[0]
    )

    try:

        # -----------------------------------------------------
        # 4. Run existing video analysis
        # -----------------------------------------------------
        result = analyze_video(
            upload_path,
            frame_folder
        )

        # Make sure result is a dictionary
        if not isinstance(result, dict):
            result = {}

        # -----------------------------------------------------
        # 5. Run advanced FFprobe + filesystem metadata analysis
        # -----------------------------------------------------
        metadata = analyze_metadata(upload_path)

        # Replace/insert metadata in final result
        result["metadata"] = metadata

        # -----------------------------------------------------
        # 6. Make sure basic audio analysis is available
        # -----------------------------------------------------
        #
        # If video_analyzer.py already produced audio_analysis,
        # keep that information.
        #
        # Otherwise create a basic audio analysis object from
        # FFprobe metadata.
        # -----------------------------------------------------

        if "audio_analysis" not in result or not isinstance(
            result.get("audio_analysis"), dict
        ):
            result["audio_analysis"] = {
                "available": metadata.get("has_audio", False),
                "has_audio": metadata.get("has_audio", False),
                "codec": metadata.get("audio_codec"),
                "channels": metadata.get("audio_channels"),
                "sample_rate": metadata.get("audio_sample_rate"),
                "message": (
                    "Audio stream detected."
                    if metadata.get("has_audio")
                    else "No audio stream detected."
                )
            }

        # -----------------------------------------------------
        # 7. Generate forensic PDF report
        # -----------------------------------------------------
        report_filename = (
            os.path.splitext(unique_filename)[0]
            + "_report.pdf"
        )

        report_path = os.path.join(
            current_app.config["REPORT_FOLDER"],
            report_filename
        )

        generate_report(
            result,
            report_path
        )

        # -----------------------------------------------------
        # 8. Add report URL
        # -----------------------------------------------------
        result["report"] = (
            f"/api/forensic/report/{report_filename}"
        )

        # -----------------------------------------------------
        # 9. Add frame base URL
        # -----------------------------------------------------
        result["frame_base_url"] = (
            f"/api/forensic/frames/"
            f"{os.path.splitext(unique_filename)[0]}"
        )

        # -----------------------------------------------------
        # 10. Return complete forensic result
        # -----------------------------------------------------
        return jsonify(result)

    except Exception as error:

        print("FORENSIC ANALYSIS ERROR:")
        print(error)

        return jsonify({
            "error": str(error)
        }), 500


@forensic_bp.route("/report/<filename>", methods=["GET"])
def download_report(filename):

    report_path = os.path.join(
        current_app.config["REPORT_FOLDER"],
        filename
    )

    if not os.path.exists(report_path):
        return jsonify({
            "error": "Report not found"
        }), 404

    return send_file(
        report_path,
        as_attachment=True
    )


@forensic_bp.route("/frames/<folder>/<filename>", methods=["GET"])
def get_frame(folder, filename):

    safe_folder = os.path.basename(folder)
    safe_filename = os.path.basename(filename)

    frame_path = os.path.join(
        current_app.config["FRAME_FOLDER"],
        safe_folder,
        safe_filename
    )

    if not os.path.exists(frame_path):
        return jsonify({
            "error": "Frame not found"
        }), 404

    return send_file(frame_path)


@forensic_bp.route(
    "/frames/<folder>/evidence/<filename>",
    methods=["GET"]
)
def get_evidence_frame(folder, filename):

    safe_folder = os.path.basename(folder)
    safe_filename = os.path.basename(filename)

    frame_path = os.path.join(
        current_app.config["FRAME_FOLDER"],
        safe_folder,
        "evidence",
        safe_filename
    )

    if not os.path.exists(frame_path):
        return jsonify({
            "error": "Evidence frame not found"
        }), 404

    return send_file(frame_path)