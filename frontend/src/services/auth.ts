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

export async function logout() {
  try {
    await api.post("/logout");
  } catch (error) {
    console.error("Logout failed:", error);
    throw error;
  }
}