import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDE4jmVe0BkV31X51zv08STmj_-oW23DRc",
  authDomain: "resume-analyzer-5cbfa.firebaseapp.com",
  projectId: "resume-analyzer-5cbfa",
  storageBucket: "resume-analyzer-5cbfa.firebasestorage.app",
  messagingSenderId: "385575974689",
  appId: "1:385575974689:web:fd73d64c318f5e3f6c7060",
  measurementId: "G-7710GC1G15"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);