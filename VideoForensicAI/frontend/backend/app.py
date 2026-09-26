import os
from flask import Flask
from flask_cors import CORS
from config import UPLOAD_FOLDER, FRAME_FOLDER, REPORT_FOLDER, MAX_FILE_SIZE
from routes.forensic_routes import forensic_bp
from services.metadata_analyzer import analyze_metadata

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["FRAME_FOLDER"] = FRAME_FOLDER
    app.config["REPORT_FOLDER"] = REPORT_FOLDER
    CORS(app)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(FRAME_FOLDER, exist_ok=True)
    os.makedirs(REPORT_FOLDER, exist_ok=True)

    app.register_blueprint(forensic_bp, url_prefix="/api/forensic")

    @app.route("/")
    def home():
        return {"application": "VideoForensic AI", "status": "running", "version": "1.0"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
