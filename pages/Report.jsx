import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api";

export default function Report() {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get(`/interview/report/${sessionId}`)
      .then((res) => setReport(res.data))
      .catch(() => setError("Report not ready yet — try refreshing in a moment."));
  }, [sessionId]);

  if (error) return <div className="p-8 text-slate-500">{error}</div>;
  if (!report) return <div className="p-8 text-slate-500">Loading report...</div>;

  const scores = [
    { label: "Technical Knowledge", value: report.technical_score },
    { label: "Communication Skills", value: report.communication_score },
    { label: "Problem Solving", value: report.problem_solving_score },
    { label: "Confidence", value: report.confidence_score },
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-800">Performance Report</h1>
          <Link to="/dashboard" className="text-indigo-600 text-sm font-medium">
            ← Back to dashboard
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <p className="text-sm text-slate-500">Overall Score</p>
          <p className="text-5xl font-bold text-indigo-600">{report.overall_score}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          {scores.map((s) => (
            <div key={s.label}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">{s.label}</span>
                <span className="text-slate-500">{s.value}/100</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full"
                  style={{ width: `${s.value}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4">
          <InfoCard title="Strengths" text={report.strengths} color="border-emerald-400" />
          <InfoCard title="Areas for Improvement" text={report.improvements} color="border-amber-400" />
          <InfoCard title="Recommended Topics to Practice" text={report.recommended_topics} color="border-indigo-400" />
        </div>
      </div>
    </div>
  );
}

function InfoCard({ title, text, color }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm p-5 border-l-4 ${color}`}>
      <h3 className="font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-sm text-slate-600">{text}</p>
    </div>
  );
}
