import api from "./api";

export async function login(username: string, password: string) {
  try {
    const response = await api.post("/login", { email: username, password });
    return response.data;
  } catch (error) {
    console.error("Login failed:", error);
    throw error;
  }
}