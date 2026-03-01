import { useNavigate } from "react-router-dom";
import { deleteProject } from "../api/projectApi";
import { useAuth } from "../context/AuthContext";

export default function ProjectCard({ project, isMember, onDeleted }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const handleDelete = async (e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete "${project.name}"? This cannot be undone.`)) return;
    try {
      await deleteProject(project.id);
      if (onDeleted) onDeleted();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete project.");
    }
  };

  return (
    <div
      onClick={() => isMember && navigate(`/projects/${project.id}`)}
      className={`bg-white rounded-xl border shadow p-5 transition-all
        ${isMember ? "cursor-pointer hover:shadow-md hover:border-blue-300" : "opacity-80"}`}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold text-gray-800 text-lg truncate">
          {project.name}
        </h3>
        <div className="flex items-center gap-2">
          {isMember && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
              Member
            </span>
          )}
          {isMember && isAdmin && (
            <button
              onClick={handleDelete}
              className="text-xs text-red-400 hover:text-red-600 font-medium"
            >
              🗑️
            </button>
          )}
        </div>
      </div>
      {project.description && (
        <p className="text-sm text-gray-500 mb-3 line-clamp-2">
          {project.description}
        </p>
      )}
      <p className="text-xs text-gray-400">
        {project.members?.length || 0} member
        {project.members?.length !== 1 ? "s" : ""} •{" "}
        {new Date(project.created_at).toLocaleDateString()}
      </p>
    </div>
  );
}