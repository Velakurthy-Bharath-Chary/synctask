import { useState } from "react";
import { useWebSocket } from "../context/WebSocketContext";

export default function NotificationBell() {
  const { notifications, clearNotifications } = useWebSocket();
  const [open, setOpen] = useState(false);
  const unread = notifications.length;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative text-white focus:outline-none"
      >
        🔔
        {unread > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border z-50 text-gray-800">
          <div className="flex justify-between items-center px-4 py-2 border-b">
            <span className="font-semibold text-sm">Notifications</span>
            {unread > 0 && (
              <button
                onClick={clearNotifications}
                className="text-xs text-blue-500 hover:underline"
              >
                Clear all
              </button>
            )}
          </div>
          <div className="max-h-64 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-center text-gray-400 text-sm py-6">
                No notifications
              </p>
            ) : (
              notifications.map((n) => (
                <div key={n.id} className="px-4 py-2 border-b hover:bg-gray-50 text-sm">
                  <span className="font-medium capitalize">
                    {n.event?.replace("_", " ")}
                  </span>
                  {n.task && <span> — {n.task.title}</span>}
                  {n.by && <span className="text-gray-500"> by {n.by}</span>}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
/*
```

Press **`Ctrl + S`** to save.

---

**What this does:**
```
Shows a 🔔 bell in the navbar

When someone creates/updates/deletes a task:
→ Red badge appears with count
→ Click bell → dropdown opens
→ Shows list of recent events like:
  "task updated — Build login page by alice"
→ Click "Clear all" to dismiss*/