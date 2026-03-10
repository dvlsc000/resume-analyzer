import React, { useState } from "react";
import Navbar from "./Navbar";
import "./AuthStyles.css";

export default function FileUpload() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  const finalScore = Number(result?.final_score ?? 0);

  const verdictClass =
    finalScore >= 75
      ? "verdict-badge verdict-strong"
      : finalScore >= 50
        ? "verdict-badge verdict-medium"
        : "verdict-badge verdict-weak";

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

      <div className="page-wrapper upload-page">
        <div className="page-content-center">
          <div className="upload-container upload-container-wide">
            <h2>Resume Matcher</h2>
            <p className="upload-subtext">
              Upload your resume and paste the job description below.
            </p>

            <div className="form-grid">
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
                  rows={12}
                />
              </div>
            </div>

            <button onClick={handleSubmit}>Submit</button>

            {status && (
              <p
                className={`status-message ${status.toLowerCase().includes("failed") ||
                    status.toLowerCase().includes("please")
                    ? "status-error"
                    : ""
                  }`}
              >
                {status}
              </p>
            )}
          </div>

          {result && (
            <div className="upload-container upload-container-wide result-container">
              <div className="result-box">
                <div className="result-header">
                  <div>
                    <h3>Match Result</h3>
                    <p className="result-file">
                      <strong>File:</strong> {result.file_name}
                    </p>
                  </div>

                  <div className={verdictClass}>
                    {result.verdict || "No verdict"}
                  </div>
                </div>

                <div className="score-grid">
                  <div className="score-card">
                    <span className="score-label">Embedding Score</span>
                    <strong>
                      {Number(result.embedding_score ?? 0).toFixed(1)}
                      <span>/100</span>
                    </strong>
                  </div>

                  <div className="score-card">
                    <span className="score-label">Gemini Score</span>
                    <strong>
                      {Number(result.gemini_score ?? 0).toFixed(1)}
                      <span>/100</span>
                    </strong>
                  </div>

                  <div className="score-card score-card-highlight">
                    <span className="score-label">Final Score</span>
                    <strong>
                      {Number(result.final_score ?? 0).toFixed(1)}
                      <span>/100</span>
                    </strong>
                  </div>
                </div>

                <div className="analysis-sections">
                  <div className="analysis-card">
                    <h4>Strengths</h4>
                    {result.strengths?.length ? (
                      <ul className="clean-list">
                        {result.strengths.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-text">No strengths found.</p>
                    )}
                  </div>

                  <div className="analysis-card">
                    <h4>Missing Requirements</h4>
                    {result.missing_requirements?.length ? (
                      <ul className="clean-list">
                        {result.missing_requirements.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-text">No missing requirements found.</p>
                    )}
                  </div>

                  <div className="analysis-card analysis-card-full">
                    <h4>Recommendations</h4>
                    {result.recommendations?.length ? (
                      <ul className="clean-list">
                        {result.recommendations.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-text">No recommendations found.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}