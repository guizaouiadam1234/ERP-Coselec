import axios, { AxiosHeaders } from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

function isMutatingMethod(method?: string): boolean {
  if (!method) {
    return false;
  }

  return ["post", "put", "patch", "delete"].includes(method.toLowerCase());
}

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

function getAuthToken(): string | null {
  return (
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token")
  );
}

api.interceptors.request.use((config) => {
  config.url = normalizeApiUrl(config.url);

  const token = getAuthToken();

  if (token) {
    const headers = AxiosHeaders.from(config.headers || {});
    headers.set("Authorization", `Bearer ${token}`);
    config.headers = headers;
  }

  return config;
});

api.interceptors.response.use(
  (response) => {
    if (isMutatingMethod(response.config.method) && typeof window !== "undefined") {
      window.dispatchEvent(new Event("notifications:refresh"));
    }

    return response;
  },
  (error) => {
    const status = error?.response?.status;
    const url = String(error?.config?.url || "");
    const isAuthEndpoint = url.includes("/login") || url.includes("/register");

    if (status === 401 && !isAuthEndpoint && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      sessionStorage.removeItem("access_token");

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
export { api };
