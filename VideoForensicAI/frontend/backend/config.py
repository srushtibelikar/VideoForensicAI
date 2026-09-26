import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
FRAME_FOLDER = os.path.join(BASE_DIR, "extracted_frames")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm", "mpeg", "mpg"}
MAX_FILE_SIZE = 500 * 1024 * 1024
