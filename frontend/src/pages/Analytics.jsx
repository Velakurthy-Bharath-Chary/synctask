import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getAnalytics } from "../api/taskApi";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, Legend, ResponsiveContainer
} from "recharts";

const STATUS_COLORS = {
  TODO: "#94a3b8",
  IN_PROGRESS: "#f59e0b",
  DONE: "#22c55e"
};
const PRIORITY_COLORS = ["#22c55e", "#f59e0b", "#ef4444"];

export default function Analytics() {
  const { projectId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalytics(projectId)
      .then((res) => setData(res.data))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen text-gray-400">
      Loading analytics...
    </div>
  );

  const statusData = data ? Object.entries(data.status_breakdown).map(([name, value]) => ({
    name: name.replace("_", " "),
    value,
    fill: STATUS_COLORS[name]
  })) : [];

  const priorityData = data ? Object.entries(data.priority_breakdown).map(([name, value], i) => ({
    name,
    value,
    fill: PRIORITY_COLORS[i]
  })) : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-sm text-gray-400 mb-1">
            <Link to={`/projects/${projectId}`} className="hover:text-blue-600">
              ← Back to Project
            </Link>
          </div>
          <h1 className="text-xl font-bold text-gray-800">Project Analytics</h1>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Tasks", value: data?.total_tasks },
            { label: "To Do", value: data?.status_breakdown?.TODO },
            { label: "In Progress", value: data?.status_breakdown?.IN_PROGRESS },
            { label: "Completed", value: data?.status_breakdown?.DONE },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white rounded-xl border shadow-sm p-5 text-center">
              <p className="text-3xl font-bold text-gray-800">{value ?? 0}</p>
              <p className="text-sm text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>

        {/* Completion Rate */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h2 className="font-semibold text-gray-700 mb-3">Completion Rate</h2>
          <div className="flex items-center gap-4">
            <div className="flex-1 bg-gray-100 rounded-full h-4">
              <div
                className="bg-green-500 h-4 rounded-full transition-all duration-700"
                style={{ width: `${data?.completion_rate || 0}%` }}
              />
            </div>
            <span className="font-bold text-green-600 text-lg">
              {data?.completion_rate || 0}%
            </span>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Status Pie Chart */}
          <div className="bg-white rounded-xl border shadow-sm p-6">
            <h2 className="font-semibold text-gray-700 mb-4">
              Task Status Distribution
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={statusData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Priority Bar Chart */}
          <div className="bg-white rounded-xl border shadow-sm p-6">
            <h2 className="font-semibold text-gray-700 mb-4">
              Tasks by Priority
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={priorityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value">
                  {priorityData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Member Productivity */}
        {data?.member_productivity?.length > 0 && (
          <div className="bg-white rounded-xl border shadow-sm p-6">
            <h2 className="font-semibold text-gray-700 mb-4">
              Member Productivity
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={data.member_productivity} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="username" width={100} />
                <Tooltip />
                <Bar dataKey="completed_tasks" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
/*

**What this does:**
```
Analytics dashboard showing:
- 4 summary cards (total, todo, in progress, done)
- Completion rate progress bar
- Pie chart → task status distribution
- Bar chart → tasks by priority
- Horizontal bar chart → member productivity
*/