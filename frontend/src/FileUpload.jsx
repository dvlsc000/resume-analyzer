import React, { useState } from "react";
import Navbar from "./Navbar";
import "./AuthStyles.css";

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      setStatus("Upload successful!");
    } catch (error) {
      setStatus("Upload failed.");
      console.error(error);
    }
  };

  return (
    <>
      <Navbar />
      <div className="page-wrapper">
        <div className="upload-container">
          <h2>Upload File</h2>
          <p className="upload-subtext">Choose your file and send it securely.</p>

          <input type="file" onChange={handleFileChange} />
          <button onClick={handleUpload}>Upload</button>

          {status && <p className="status-message">{status}</p>}
        </div>
      </div>
    </>
  );
}