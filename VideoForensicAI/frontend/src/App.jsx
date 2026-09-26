import React, { useState } from "react";
import UploadBox from "./components/UploadBox";
import ResultCard from "./components/ResultCard";
import FrameGallery from "./components/FrameGallery";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="app">
      <header>
        <h1>VideoForensic AI</h1>
        <p>Digital Video Forensic Analysis System</p>
      </header>

      <main>
        <UploadBox onResult={setResult} />

        {result && (
          <>
            <ResultCard result={result} />
            <FrameGallery result={result} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
