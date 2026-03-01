import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import NotificationBell from "./NotificationBell";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-blue-600 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <Link to="/" className="text-xl font-bold tracking-wide">
        ⚡ SyncTask
      </Link>
      {user && (
        <div className="flex items-center gap-4">
          <span className="text-sm bg-blue-800 px-2 py-1 rounded capitalize">
            {user.role}
          </span>
          <span className="text-sm">{user.username}</span>
          <NotificationBell />
          <button
            onClick={handleLogout}
            className="bg-white text-blue-600 px-3 py-1 rounded text-sm font-medium hover:bg-blue-50"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}