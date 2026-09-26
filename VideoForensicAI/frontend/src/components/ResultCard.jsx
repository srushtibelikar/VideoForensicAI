import React from "react";

const API = "http://localhost:5000";

function ResultCard({ result = {} }) {
  // Safely handle missing sections from the backend
  const metadata = result.metadata || {};
  const frame = result.frame_analysis || {};
  const audio = result.audio_analysis || {};
  const tampering = result.tampering_detection || {};

  // Safely handle arrays
  const evidenceFrames = Array.isArray(frame.evidence_frames)
    ? frame.evidence_frames
    : [];

  const suspiciousSegments = Array.isArray(frame.suspicious_segments)
    ? frame.suspicious_segments
    : [];

  const highChangeFrames = Array.isArray(frame.high_change_frames)
    ? frame.high_change_frames
    : [];

  const blurFrames = Array.isArray(frame.blur_frames)
    ? frame.blur_frames
    : [];

  const indicators = Array.isArray(tampering.indicators)
    ? tampering.indicators
    : [];

  const audioStreams = Array.isArray(audio.streams)
    ? audio.streams
    : [];

  const classification = result.classification || "Unknown";

  const riskClass = classification
    .toLowerCase()
    .replace(/\s+/g, "-");

  return (
    <div className="result-card">

      {/* ================= HEADER ================= */}
      <div className="result-header">
        <div>
          <p className="eyebrow">ANALYSIS COMPLETE</p>
          <h2>Forensic Analysis Result</h2>
        </div>

        <div className={`risk-badge risk-${riskClass}`}>
          {classification}
        </div>
      </div>

      {/* ================= SCORE GRID ================= */}
      <div className="score-grid">

        <div className="score-box">
          <span>Risk Score</span>
          <strong>
            {result.risk_score ?? 0}/100
          </strong>
        </div>

        <div className="score-box">
          <span>Indicators</span>
          <strong>
            {tampering.indicator_count ?? indicators.length}
          </strong>
        </div>

        <div className="score-box">
          <span>Evidence Frames</span>
          <strong>
            {evidenceFrames.length}
          </strong>
        </div>

        <div className="score-box">
          <span>Segments</span>
          <strong>
            {suspiciousSegments.length}
          </strong>
        </div>

      </div>

      {/* ================= METADATA ================= */}
      <h3>Advanced Metadata</h3>

      <div className="info-grid">

        <p>
          <strong>Filename</strong>
          {metadata.filename || "Unknown"}
        </p>

        <p>
          <strong>Resolution</strong>
          {metadata.resolution || "Unknown"}
        </p>

        <p>
          <strong>FPS</strong>
          {metadata.fps ?? "-"}
        </p>

        <p>
          <strong>Frame count</strong>
          {metadata.frame_count ?? "-"}
        </p>

        <p>
          <strong>Duration</strong>
          {metadata.duration_seconds ?? "-"} sec
        </p>

        <p>
          <strong>File size</strong>
          {metadata.file_size_mb ?? "-"} MB
        </p>

        <p>
          <strong>Container</strong>
          {metadata.container || "Unknown"}
        </p>

        <p>
          <strong>Video codec</strong>
          {metadata.codec || "Unknown"}
        </p>

        <p>
          <strong>Pixel format</strong>
          {metadata.pixel_format || "Unknown"}
        </p>

        <p>
          <strong>Creation time</strong>
          {metadata.creation_time || "Unknown"}
        </p>

        <p>
          <strong>Audio</strong>
          {metadata.has_audio
            ? `${metadata.audio_codec || "Unknown"} / ${
                metadata.audio_channels ?? "-"
              } channel(s)`
            : "Not detected"}
        </p>

        <p>
          <strong>Metadata source</strong>
          {metadata.metadata_source || "Unknown"}
        </p>

      </div>

      {/* ================= FRAME ANALYSIS ================= */}
      <h3>Frame-Level Analysis</h3>

      <div className="info-grid">

        <p>
          <strong>Sampled frames</strong>
          {frame.sample_count ?? "-"}
        </p>

        <p>
          <strong>Average difference</strong>
          {frame.average_frame_difference ?? "-"}
        </p>

        <p>
          <strong>Repeated frames</strong>
          {frame.duplicate_frame_count ?? 0}
        </p>

        <p>
          <strong>Abrupt changes</strong>
          {highChangeFrames.length}
        </p>

        <p>
          <strong>Low-blur frames</strong>
          {blurFrames.length}
        </p>

        <p>
          <strong>Analysis method</strong>
          {frame.analysis_method || "Not available"}
        </p>

      </div>

      {/* ================= TAMPERING ================= */}
      <h3>Tampering Detection Indicators</h3>

      <div className="indicator-list">

        {indicators.length === 0 ? (
          <p className="ok">
            No configured automated indicators were triggered.
          </p>
        ) : (
          indicators.map((item, i) => (
            <div
              className={`indicator ${item.severity || "medium"}`}
              key={i}
            >
              <span>
                {item.type || "Indicator"}
              </span>

              <p>
                {item.message || "No description available."}
              </p>
            </div>
          ))
        )}

      </div>

      {/* ================= AUDIO ================= */}
      <h3>Audio Analysis</h3>

      <p className="audio-status">
        {audio.status || "Audio analysis information unavailable."}
      </p>

      {audioStreams.length > 0 && (
        <div className="table-wrap">

          <table>

            <thead>
              <tr>
                <th>Codec</th>
                <th>Sample Rate</th>
                <th>Channels</th>
                <th>Duration</th>
              </tr>
            </thead>

            <tbody>

              {audioStreams.map((s, i) => (
                <tr key={i}>

                  <td>
                    {s.codec_name || "Unknown"}
                  </td>

                  <td>
                    {s.sample_rate || "-"} Hz
                  </td>

                  <td>
                    {s.channels || "-"}
                  </td>

                  <td>
                    {s.duration || "-"} sec
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>
      )}

      {/* ================= SUSPICIOUS SEGMENTS ================= */}
      <h3>Suspicious Segments</h3>

      {suspiciousSegments.length > 0 ? (

        <div className="table-wrap">

          <table>

            <thead>
              <tr>
                <th>Start</th>
                <th>End</th>
                <th>Reason</th>
              </tr>
            </thead>

            <tbody>

              {suspiciousSegments.map((s, i) => (
                <tr key={i}>

                  <td>
                    {s.start_seconds ?? "-"}s
                  </td>

                  <td>
                    {s.end_seconds ?? "-"}s
                  </td>

                  <td>
                    {s.reason || "Suspicious activity"}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>

      ) : (

        <p className="ok">
          No suspicious segments detected by the configured heuristics.
        </p>

      )}

      {/* ================= HASH ================= */}
      <p className="hash">
        <strong>SHA-256:</strong>{" "}
        {result.sha256 || "Not available"}
      </p>

      {/* ================= DISCLAIMER ================= */}
      <p className="disclaimer">
        {tampering.disclaimer ||
          "Automated forensic indicators are heuristic and should be reviewed with additional evidence."}
      </p>

      {/* ================= REPORT ================= */}
      {result.report && (
        <a
          className="report-link"
          href={`${API}${result.report}`}
          target="_blank"
          rel="noreferrer"
        >
          Open / Download Forensic Report (PDF)
        </a>
      )}

    </div>
  );
}

export default ResultCard;

