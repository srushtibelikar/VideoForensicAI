import React, { useState } from "react";
import { analyzeVideo } from "../api";

function UploadBox({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      setError("Please select a video.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await analyzeVideo(file);
      onResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-box">
      <h2>Upload Video Evidence</h2>
      <p>Select a video for forensic analysis.</p>

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Video"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default UploadBox;
