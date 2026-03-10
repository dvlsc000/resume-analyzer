import React, { useState } from "react";
import Navbar from "./Navbar";
import "./AuthStyles.css";

export default function FileUpload() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  const handleResumeChange = (event) => {
    setResume(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!resume) {
      setStatus("Please upload your resume.");
      return;
    }

    if (!jobDescription.trim()) {
      setStatus("Please paste the job description.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("jobDescription", jobDescription);

    try {
      setStatus("Analyzing resume against the job description...");
      setResult(null);

      const response = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Submission failed");
      }

      setResult(data);
      setStatus("Analysis completed successfully!");
    } catch (error) {
      setStatus(error.message || "Submission failed.");
      console.error(error);
    }
  };

  return (
    <>
      <Navbar />
      <div className="page-wrapper">
        <div className="upload-container">
          <h2>Resume Matcher</h2>
          <p className="upload-subtext">
            Upload your resume and paste the job description below.
          </p>

          <div className="form-group">
            <label className="input-label">Upload Resume</label>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleResumeChange}
            />
            {resume && <p className="file-name">Selected: {resume.name}</p>}
          </div>

          <div className="form-group">
            <label className="input-label">Job Description</label>
            <textarea
              className="job-description-box"
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={10}
            />
          </div>

          <button onClick={handleSubmit}>Submit</button>

          {status && <p className="status-message">{status}</p>}

          {result && (
            <div className="result-box" style={{ marginTop: "20px", textAlign: "left" }}>
              <h3>Match Result</h3>
              <p><strong>File:</strong> {result.file_name}</p>
              <p><strong>Embedding Score:</strong> {result.embedding_score}/100</p>
              <p><strong>Gemini Score:</strong> {result.gemini_score}/100</p>
              <p><strong>Final Score:</strong> {result.final_score}/100</p>
              <p><strong>Verdict:</strong> {result.verdict}</p>

              <h4>Strengths</h4>
              <ul>
                {result.strengths?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <h4>Missing Requirements</h4>
              <ul>
                {result.missing_requirements?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <h4>Recommendations</h4>
              <ul>
                {result.recommendations?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
}