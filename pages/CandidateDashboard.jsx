import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const JOB_ROLES = [
  "Software Engineer",
  "Data Scientist",
  "AI/ML Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
];
const INTERVIEW_TYPES = ["Technical", "HR", "Mixed"];
const DIFFICULTIES = ["Easy", "Medium", "Hard"];

export default function CandidateDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [form, setForm] = useState({
    job_role: JOB_ROLES[0],
    interview_type: INTERVIEW_TYPES[0],
    difficulty: DIFFICULTIES[0],
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const loadDashboard = async () => {
    const res = await api.get("/candidate/dashboard");
    setDashboard(res.data);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/candidate/resume/upload", formData);
      setResumeId(res.data.resume_id);
      loadDashboard();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const startInterview = async () => {
    if (!resumeId) {
      setError("Upload your resume first");
      return;
    }
    try {
      const res = await api.post("/interview/start", { resume_id: resumeId, ...form });
      navigate(`/interview/${res.data.session_id}`, { state: { firstQuestion: res.data.question } });
    } catch (err) {
      setError(err.response?.data?.detail || "Could not start interview");
    }
  };

  if (!dashboard) return <div className="p-8 text-slate-500">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Hi, {dashboard.name}</h1>
          <p className="text-slate-500 text-sm">{dashboard.email}</p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <StatCard label="Resume" value={dashboard.resume_uploaded ? "Uploaded" : "Missing"} />
          <StatCard label="Interviews Completed" value={dashboard.interviews_completed} />
          <StatCard label="Latest Score" value={dashboard.latest_score ?? "-"} />
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          <h2 className="font-semibold text-slate-800">Start a New Interview</h2>

          <div>
            <label className="text-sm text-slate-600">Resume (PDF)</label>
            <input type="file" accept="application/pdf" onChange={handleUpload} className="block mt-1 text-sm" />
            {uploading && <p className="text-sm text-slate-400">Uploading...</p>}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <Select label="Job Role" value={form.job_role} options={JOB_ROLES}
              onChange={(v) => setForm({ ...form, job_role: v })} />
            <Select label="Interview Type" value={form.interview_type} options={INTERVIEW_TYPES}
              onChange={(v) => setForm({ ...form, interview_type: v })} />
            <Select label="Difficulty" value={form.difficulty} options={DIFFICULTIES}
              onChange={(v) => setForm({ ...form, difficulty: v })} />
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            onClick={startInterview}
            className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            Start Interview
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold text-slate-800 mb-3">Previous Reports</h2>
          {dashboard.reports.length === 0 && <p className="text-sm text-slate-400">No interviews yet.</p>}
          <ul className="divide-y divide-slate-100">
            {dashboard.reports.map((r) => (
              <li key={r.session_id} className="py-2 flex justify-between items-center text-sm">
                <span>{r.job_role} — {r.status}</span>
                {r.overall_score != null ? (
                  <button
                    className="text-indigo-600 font-medium"
                    onClick={() => navigate(`/report/${r.session_id}`)}
                  >
                    Score: {r.overall_score} → View Report
                  </button>
                ) : (
                  <span className="text-slate-400">In progress</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-xl font-semibold text-slate-800">{value}</p>
    </div>
  );
}

function Select({ label, value, options, onChange }) {
  return (
    <div>
      <label className="text-sm text-slate-600">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-slate-300 rounded-lg px-2 py-1.5 text-sm mt-1"
      >
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}
