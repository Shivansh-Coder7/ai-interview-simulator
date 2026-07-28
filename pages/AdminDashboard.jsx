import { useEffect, useState } from "react";
import api from "../api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/admin/stats").then((res) => setStats(res.data));
  }, []);

  if (!stats) return <div className="p-8 text-slate-500">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-slate-800">Admin Dashboard</h1>

        <div className="grid grid-cols-3 gap-4">
          <StatCard label="Total Users" value={stats.total_users} />
          <StatCard label="Total Interviews" value={stats.total_interviews} />
          <StatCard label="Average Score" value={stats.avg_score} />
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold text-slate-800 mb-3">Most Selected Job Roles</h2>
          <ul className="space-y-2">
            {stats.most_selected_roles.map((r) => (
              <li key={r.role} className="flex justify-between text-sm">
                <span className="text-slate-700">{r.role}</span>
                <span className="text-slate-500">{r.count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold text-slate-800 mb-3">Recent Interview Activity</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b">
                <th className="py-2">Job Role</th>
                <th>Type</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_activity.map((a) => (
                <tr key={a.session_id} className="border-b last:border-0">
                  <td className="py-2">{a.job_role}</td>
                  <td>{a.interview_type}</td>
                  <td>{a.status}</td>
                  <td>{new Date(a.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
