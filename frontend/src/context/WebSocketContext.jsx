import { createContext, useContext, useRef, useState, useCallback, useEffect } from "react";
import { useAuth } from "./AuthContext";
import { getMyProjects } from "../api/projectApi";

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const { token } = useAuth();
  const socketsRef = useRef(new Map());
  const [notifications, setNotifications] = useState([]);
  const listenersRef = useRef({});

  const subscribe = useCallback((event, callback) => {
    if (!listenersRef.current[event]) {
      listenersRef.current[event] = new Set();
    }
    listenersRef.current[event].add(callback);
    return () => listenersRef.current[event]?.delete(callback);
  }, []);

  const getWsBaseUrl = useCallback(() => {
    const rawConfigured = process.env.REACT_APP_WS_URL || "ws://localhost:8000/api";
    const configured = rawConfigured.endsWith("/api")
      ? rawConfigured
      : `${rawConfigured.replace(/\/+$/, "")}/api`;
    const hostname = window.location.hostname;
    const isLocalHostInConfig =
      configured.includes("://localhost") || configured.includes("://127.0.0.1");

    if (hostname && hostname !== "localhost" && hostname !== "127.0.0.1" && isLocalHostInConfig) {
      return configured
        .replace("://localhost", `://${hostname}`)
        .replace("://127.0.0.1", `://${hostname}`);
    }

    return configured;
  }, []);

  const openProjectSocket = useCallback((projectId) => {
    if (!token) return;
    const key = String(projectId);
    if (!key || socketsRef.current.has(key)) return;

    const wsUrl = `${getWsBaseUrl()}/ws/${key}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[WS] Connected to project ${key}`);
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
      console.log(`[WS] Connection closed for project ${key}`);
      clearInterval(ws._pingInterval);
      if (socketsRef.current.get(key) === ws) {
        socketsRef.current.delete(key);
      }
    };

    ws.onerror = (err) => {
      console.error("[WS] Error:", err);
    };

    socketsRef.current.set(key, ws);
  }, [token, getWsBaseUrl]);

  const connectToProject = useCallback((projectId) => {
    openProjectSocket(projectId);
  }, [openProjectSocket]);

  const disconnectFromProject = useCallback((projectId) => {
    if (projectId) {
      const key = String(projectId);
      const ws = socketsRef.current.get(key);
      if (ws) {
        ws.close();
        socketsRef.current.delete(key);
      }
      return;
    }

    for (const [key, ws] of socketsRef.current.entries()) {
      ws.close();
      socketsRef.current.delete(key);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;

    const syncSockets = async () => {
      if (!token) {
        disconnectFromProject();
        return;
      }

      try {
        const res = await getMyProjects();
        if (isCancelled) return;

        const ids = new Set((res.data || []).map((p) => String(p.id)));

        for (const projectId of ids) {
          openProjectSocket(projectId);
        }

        for (const key of Array.from(socketsRef.current.keys())) {
          if (!ids.has(key)) {
            const ws = socketsRef.current.get(key);
            if (ws) ws.close();
            socketsRef.current.delete(key);
          }
        }
      } catch (err) {
        console.error("[WS] Failed to sync project sockets", err);
      }
    };

    syncSockets();
    const intervalId = token ? setInterval(syncSockets, 30000) : null;

    return () => {
      isCancelled = true;
      if (intervalId) clearInterval(intervalId);
    };
  }, [token, openProjectSocket, disconnectFromProject]);

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
