import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

function normalizeApiUrl(url?: string): string | undefined {
  if (!url || typeof url !== "string") {
    return url;
  }

  // Skip absolute URLs and auth endpoints.
  if (/^https?:\/\//i.test(url) || url.startsWith("/login") || url.startsWith("/register")) {
    return url;
  }

  const [rawPath = "", query = ""] = url.split("?");
  const path = rawPath || "/";

  if (path.endsWith("/")) {
    return url;
  }

  const normalized = `${path}/`;
  return query ? `${normalized}?${query}` : normalized;
}

api.interceptors.request.use((config) => {
  config.url = normalizeApiUrl(config.url);

  const token =
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token");

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;
export { api };
