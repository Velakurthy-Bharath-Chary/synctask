import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getProject } from "../api/projectApi";
import { getTasks, createTask, updateTask, deleteTask } from "../api/taskApi";
import { useWebSocket } from "../context/WebSocketContext";
import TaskCard from "../components/TaskCard";
import TaskModal from "../components/TaskModal";

const COLUMNS = ["TODO", "IN_PROGRESS", "DONE"];
const COLUMN_LABELS = {
  TODO: "To Do",
  IN_PROGRESS: "In Progress",
  DONE: "Done",
};

export default function ProjectView() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { connectToProject, disconnectFromProject, subscribe } = useWebSocket();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingTask, setEditingTask] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [projRes, taskRes] = await Promise.all([
        getProject(parseInt(projectId)),
        getTasks(parseInt(projectId)),
      ]);
      setProject(projRes.data);
      setTasks(taskRes.data);
    } catch (err) {
      setError("Failed to load project. You may not have access.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchData();
    connectToProject(parseInt(projectId));

    // Listen for real-time task events
    const unsubCreate = subscribe("task_created", (msg) => {
      setTasks((prev) => {
        if (prev.find((t) => t.id === msg.task.id)) return prev;
        return [...prev, { ...msg.task }];
      });
    });

    const unsubUpdate = subscribe("task_updated", (msg) => {
      setTasks((prev) =>
        prev.map((t) => (t.id === msg.task.id ? { ...t, ...msg.task } : t))
      );
    });

    const unsubDelete = subscribe("task_deleted", (msg) => {
      setTasks((prev) => prev.filter((t) => t.id !== msg.task_id));
    });

    return () => {
      disconnectFromProject();
      unsubCreate();
      unsubUpdate();
      unsubDelete();
    };
  }, [projectId, connectToProject, disconnectFromProject, subscribe, fetchData]);

  const handleSaveTask = async (formData) => {
    try {
      if (editingTask?.id) {
        await updateTask(editingTask.id, formData);
      } else {
        await createTask(parseInt(projectId), formData);
      }
      setShowModal(false);
      setEditingTask(null);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to save task.");
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Delete this task?")) return;
    try {
      await deleteTask(taskId);
    } catch (err) {
      alert("Failed to delete task.");
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-gray-400 text-lg">Loading project...</div>
    </div>
  );

  if (error) return (
    <div className="flex items-center justify-center min-h-screen flex-col gap-4">
      <div className="text-red-500">{error}</div>
      <button onClick={() => navigate("/")} className="text-blue-600 hover:underline">
        Back to Dashboard
      </button>
    </div>
  );

  const tasksByStatus = COLUMNS.reduce((acc, status) => {
    acc[status] = tasks.filter((t) => t.status === status);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Project Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <div className="text-sm text-gray-400 mb-1">
              <Link to="/" className="hover:text-blue-600">
                Dashboard
              </Link>{" "}
              / {project?.name}
            </div>
            <h1 className="text-xl font-bold text-gray-800">{project?.name}</h1>
            {project?.description && (
              <p className="text-sm text-gray-500 mt-0.5">{project.description}</p>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              👥 {project?.members?.length} member
              {project?.members?.length !== 1 ? "s" : ""}
            </div>
            <Link
              to={`/projects/${projectId}/analytics`}
              className="text-sm text-blue-600 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-50"
            >
              📊 Analytics
            </Link>
            <button
              onClick={() => { setEditingTask(null); setShowModal(true); }}
              className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700"
            >
              + Add Task
            </button>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {COLUMNS.map((status) => (
            <div key={status} className="bg-white rounded-xl border shadow-sm">
              <div className="px-4 py-3 border-b flex justify-between items-center">
                <h2 className="font-semibold text-gray-700">
                  {COLUMN_LABELS[status]}
                </h2>
                <span className="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-0.5 rounded-full">
                  {tasksByStatus[status].length}
                </span>
              </div>
              <div className="p-3 space-y-3 min-h-32">
                {tasksByStatus[status].length === 0 ? (
                  <p className="text-center text-gray-300 text-sm py-6">
                    No tasks
                  </p>
                ) : (
                  tasksByStatus[status].map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      members={project?.members}
                      onEdit={(task) => { setEditingTask(task); setShowModal(true); }}
                      onDelete={handleDeleteTask}
                    />
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Team Members */}
      <div className="max-w-7xl mx-auto px-4 pb-8">
        <div className="bg-white rounded-xl border shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3">Team Members</h3>
          <div className="flex flex-wrap gap-2">
            {project?.members?.map((m) => (
              <div
                key={m.id}
                className="flex items-center gap-2 bg-gray-50 rounded-full px-3 py-1"
              >
                <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold">
                  {m.user.username[0].toUpperCase()}
                </div>
                <span className="text-sm text-gray-700">{m.user.username}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Task Modal */}
      {showModal && (
        <TaskModal
          task={editingTask}
          members={project?.members}
          onSave={handleSaveTask}
          onClose={() => { setShowModal(false); setEditingTask(null); }}
        />
      )}
    </div>
  );
}
