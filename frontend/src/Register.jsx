import { useState } from "react";
import { auth } from "./firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./AuthStyles.css";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      console.log("Registered:", userCredential.user);
      alert("Registration successful");
      navigate("/");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <>
      <Navbar />
      <div className="page-wrapper">
        <div className="auth-container">
          <h2>Create Account</h2>
          <p className="auth-subtext">Join and start uploading in style.</p>

          <form onSubmit={handleRegister}>
            <input
              type="email"
              placeholder="Email"
              onChange={(e) => setEmail(e.target.value)}
            />

            <input
              type="password"
              placeholder="Password"
              onChange={(e) => setPassword(e.target.value)}
            />

            <button type="submit">Register</button>
          </form>

          <p>Already have an account?</p>
          <button onClick={() => navigate("/")}>Go to Login</button>
        </div>
      </div>
    </>
  );
}

export default Register;