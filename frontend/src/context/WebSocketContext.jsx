import { createContext, useContext, useRef, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const { token } = useAuth();
  const socketRef = useRef(null);
  const [notifications, setNotifications] = useState([]);
  const listenersRef = useRef({});

  const subscribe = useCallback((event, callback) => {
    if (!listenersRef.current[event]) {
      listenersRef.current[event] = new Set();
    }
    listenersRef.current[event].add(callback);
    return () => listenersRef.current[event]?.delete(callback);
  }, []);

  const connectToProject = useCallback((projectId) => {
    if (!token) return;

    // Close existing connection
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsUrl = `${process.env.REACT_APP_WS_URL || "ws://localhost:8000"}/ws/${projectId}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[WS] Connected to project ${projectId}`);
      // Send ping every 30 seconds to keep connection alive
      ws._pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send("ping");
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
       if (event.data === "pong") return;
const message = JSON.parse(event.data);

        // Fire all subscribers for this event
        const handlers = listenersRef.current[message.event];
        if (handlers) {
          handlers.forEach((cb) => cb(message));
        }

        // Add to notifications bell
        if (message.event !== "connected") {
          setNotifications((prev) => [
            { id: Date.now(), ...message },
            ...prev.slice(0, 19),
          ]);
        }
      } catch (err) {
        console.error("[WS] Parse error:", err);
      }
    };

    ws.onclose = () => {
      console.log("[WS] Connection closed");
      clearInterval(ws._pingInterval);
    };

    ws.onerror = (err) => {
      console.error("[WS] Error:", err);
    };

    socketRef.current = ws;
  }, [token]);

  const disconnectFromProject = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  }, []);

  const clearNotifications = () => setNotifications([]);

  return (
    <WebSocketContext.Provider value={{
      connectToProject,
      disconnectFromProject,
      subscribe,
      notifications,
      clearNotifications,
    }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export const useWebSocket = () => useContext(WebSocketContext);
/*
**What this does:**
```
Manages the WebSocket connection globally:

connectToProject(id) → opens WS connection
disconnectFromProject() → closes connection
subscribe(event, callback) → listen for events
notifications → list of recent events for bell

When backend broadcasts "task_updated":
→ this context receives it
→ fires all subscribers
→ ProjectView updates instantly!*/