# VideoForensic AI

An AI-assisted digital video forensic analysis MVP with evidence hashing, metadata inspection, frame-level analysis, repeated-frame detection, suspicious-segment detection, audio stream inspection, visual evidence, tampering indicators, risk scoring, and PDF reporting.

## Features

- Video upload with file validation
- SHA-256 evidence hashing
- Advanced container/video metadata using FFprobe when available, with OpenCV fallback
- Frame extraction at approximately 1 frame per second
- Per-frame brightness, contrast, blur, and edge-density metrics
- Perceptual-hash repeated-frame detection
- Abrupt frame-change detection
- Suspicious segment grouping with timestamps
- Automatic visual evidence-frame extraction
- Audio stream inspection (codec, sample rate, channels, duration)
- Heuristic tampering-indicator engine
- Risk score and risk classification
- Detailed forensic PDF report
- React dashboard with evidence gallery

## Important forensic note

Automated indicators are not proof that a video is fake or manipulated. This project is an educational/MVP forensic aid. Findings should be corroborated with the original evidence, chain-of-custody records, validated forensic tools, and qualified expert examination.

## FFmpeg / FFprobe

FFprobe is recommended for advanced metadata and audio stream inspection. If FFprobe is not installed, the application still runs and falls back to OpenCV for basic metadata. On Windows, make sure `ffprobe.exe` is on PATH and verify with:

```powershell
ffprobe -version
```

## Backend

```powershell
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend: http://localhost:5000

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## One-command startup

From the project root, double-click `start_project.bat` or run:

```powershell
.\start_project.bat
```

It creates the virtual environment if needed, installs backend dependencies, and opens backend/frontend in separate terminals.
