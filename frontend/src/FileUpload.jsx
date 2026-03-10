import React, { useState } from "react";
import Navbar from "./Navbar";
import "./AuthStyles.css";

export default function FileUpload() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  const finalScore = Number(result?.final_score ?? 0);
  const atsScore = Number(result?.ats_analysis?.ats_score ?? 0);

  const verdictClass =
    finalScore >= 75
      ? "verdict-badge verdict-strong"
      : finalScore >= 50
        ? "verdict-badge verdict-medium"
        : "verdict-badge verdict-weak";

  const atsClass =
    atsScore >= 85
      ? "verdict-badge verdict-strong"
      : atsScore >= 70
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

  const contactChecks = result?.ats_analysis?.contact_checks || {};

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
                className={`status-message ${
                  status.toLowerCase().includes("failed") ||
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

                  <div className="score-card">
                    <span className="score-label">ATS Score</span>
                    <strong>
                      {atsScore.toFixed(1)}
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

                <div className="analysis-sections">
                  <div className="analysis-card">
                    <div className="card-header-row">
                      <h4>ATS Readability</h4>
                      <div className={atsClass}>
                        {result.ats_analysis?.ats_verdict || "No ATS verdict"}
                      </div>
                    </div>

                    <p className="ats-score-text">
                      ATS Parseability Score:{" "}
                      <strong>{atsScore.toFixed(1)}/100</strong>
                    </p>

                    <h5>Detected Sections</h5>
                    {result.ats_analysis?.detected_sections?.length ? (
                      <div className="tag-wrap">
                        {result.ats_analysis.detected_sections.map((section, idx) => (
                          <span key={idx} className="tag-chip">
                            {section}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="empty-text">No clear sections detected.</p>
                    )}
                  </div>

                  <div className="analysis-card">
                    <h4>Contact Checks</h4>
                    <ul className="clean-list">
                      <li>Email: {contactChecks.email ? "Detected" : "Missing"}</li>
                      <li>Phone: {contactChecks.phone ? "Detected" : "Missing"}</li>
                      <li>LinkedIn: {contactChecks.linkedin ? "Detected" : "Missing"}</li>
                      <li>GitHub: {contactChecks.github ? "Detected" : "Missing"}</li>
                      <li>Location: {contactChecks.location ? "Detected" : "Missing"}</li>
                    </ul>
                  </div>

                  <div className="analysis-card">
                    <h4>Formatting Warnings</h4>
                    {result.ats_analysis?.format_warnings?.length ? (
                      <ul className="clean-list">
                        {result.ats_analysis.format_warnings.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-text">No major formatting warnings found.</p>
                    )}
                  </div>

                  <div className="analysis-card analysis-card-full">
                    <h4>ATS Improvements</h4>
                    {result.ats_analysis?.ats_improvements?.length ? (
                      <ul className="clean-list">
                        {result.ats_analysis.ats_improvements.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="empty-text">No ATS improvements suggested.</p>
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