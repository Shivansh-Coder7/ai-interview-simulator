import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Login() {
  const [role, setRole] = useState("candidate");
  const [mode, setMode] = useState("login"); // login | signup
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const url =
        role === "admin"
          ? "/admin/login"
          : mode === "signup"
          ? "/candidate/signup"
          : "/candidate/login";

      const payload =
        mode === "signup" && role === "candidate"
          ? { name: form.name, email: form.email, password: form.password }
          : { email: form.email, password: form.password };

      const res = await api.post(url, payload);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("role", role);
      localStorage.setItem("name", res.data.name || "");

      navigate(role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white shadow-md rounded-xl p-8 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-slate-800 mb-1">AI Interview Simulator</h1>
        <p className="text-slate-500 mb-6 text-sm">
          {role === "admin" ? "Admin login" : mode === "signup" ? "Create your account" : "Welcome back"}
        </p>

        <div className="flex gap-2 mb-6">
          <button
            className={`flex-1 py-1.5 rounded-lg text-sm font-medium ${
              role === "candidate" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600"
            }`}
            onClick={() => setRole("candidate")}
            type="button"
          >
            Candidate
          </button>
          <button
            className={`flex-1 py-1.5 rounded-lg text-sm font-medium ${
              role === "admin" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600"
            }`}
            onClick={() => setRole("admin")}
            type="button"
          >
            Admin
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && role === "candidate" && (
            <input
              name="name"
              placeholder="Full name"
              value={form.name}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
              required
            />
          )}
          <input
            name="email"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
            required
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
            required
          />

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            {mode === "signup" ? "Sign Up" : "Log In"}
          </button>
        </form>

        {role === "candidate" && (
          <p className="text-sm text-slate-500 mt-4 text-center">
            {mode === "login" ? "New here?" : "Already have an account?"}{" "}
            <button
              className="text-indigo-600 font-medium"
              onClick={() => setMode(mode === "login" ? "signup" : "login")}
            >
              {mode === "login" ? "Sign up" : "Log in"}
            </button>
          </p>
        )}
      </div>
    </div>
  );
}
