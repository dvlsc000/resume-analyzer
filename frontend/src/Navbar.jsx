import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { auth } from "./firebase";
import { signOut } from "firebase/auth";
import "./AuthStyles.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = auth.currentUser;

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
      alert("Failed to log out.");
    }
  };

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate("/upload")}>
        ResumePulse
      </div>

      <div className="navbar-links">
        <button
          className={`nav-btn ${location.pathname === "/upload" ? "active" : ""}`}
          onClick={() => navigate("/upload")}
        >
          Upload
        </button>

        <button className="nav-btn logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}