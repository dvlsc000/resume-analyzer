import React, { useState } from "react";
import Navbar from "./Navbar";
import "./AuthStyles.css";

export default function FileUpload() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [status, setStatus] = useState("");

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
      setStatus("Uploading resume and job description...");

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Submission failed");
      }

      setStatus("Resume and job description submitted successfully!");
    } catch (error) {
      setStatus("Submission failed.");
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
            <input type="file" accept=".pdf,.doc,.docx" onChange={handleResumeChange} />
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
        </div>
      </div>
    </>
  );
}