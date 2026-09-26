const API_URL = "http://localhost:5000/api/forensic";

export async function analyzeVideo(file) {
  const formData = new FormData();
  formData.append("video", file);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Analysis failed");
  }

  return data;
}
