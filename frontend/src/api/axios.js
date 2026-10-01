import axios from "axios";

const getApiBaseUrl = () => {
  const configured = process.env.REACT_APP_API_URL || "http://localhost:8000/api";
  const hostname = window.location.hostname;
  const isLocalHostInConfig =
    configured.includes("://localhost") || configured.includes("://127.0.0.1");

  if (hostname && hostname !== "localhost" && hostname !== "127.0.0.1" && isLocalHostInConfig) {
    return configured
      .replace("://localhost", `://${hostname}`)
      .replace("://127.0.0.1", `://${hostname}`);
  }

  return configured;
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    return Promise.reject(err);
  }
);

export default api;
