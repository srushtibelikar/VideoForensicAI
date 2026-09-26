import React from "react";

function FrameGallery({ result }) {
  const frames = result?.frame_analysis?.sampled_frames || [];
  const evidence = result?.frame_analysis?.evidence_frames || [];
  const baseUrl = "http://localhost:5000";

  return (
    <div className="frame-gallery">
      <h2>Visual Evidence</h2>
      <p className="muted">Sampled frames and automatically selected evidence frames for review.</p>

      {evidence.length > 0 && <>
        <h3>Suspicious Evidence Frames</h3>
        <div className="frames evidence-frames">
          {evidence.map((frame) => (
            <div className="frame evidence" key={`${frame.frame_number}-${frame.filename}`}>
              <img src={`${baseUrl}${result.frame_base_url}/evidence/${frame.filename}`} alt={`Evidence frame ${frame.frame_number}`} loading="lazy" />
              <p>Frame {frame.frame_number} · {frame.timestamp_seconds}s</p>
              <small>{frame.reason} · Δ {frame.difference}</small>
            </div>
          ))}
        </div>
      </>}

      <h3>Sampled Frames</h3>
      <div className="frames">
        {frames.map((frame) => (
          <div className="frame" key={frame.frame_number}>
            <img src={`${baseUrl}${result.frame_base_url}/${frame.filename}`} alt={`Frame ${frame.frame_number}`} loading="lazy" />
            <p>Frame {frame.frame_number} · {frame.timestamp_seconds}s</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FrameGallery;
