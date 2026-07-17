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

export async function changePassword(email: string, oldPassword: string, newPassword: string) {
  try {
    const response = await api.post("/change-password", {
      email,
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  } catch (error) {
    console.error("Change password failed:", error);
    throw error;
  }
}