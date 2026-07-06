import api from "./api";

export type TicketCategory = "Leave" | "Purchase" | "Facility" | "IT";

export type TicketCreatePayload = {
  title: string;
  description: string;
  category: TicketCategory;
  meta_data?: Record<string, unknown>;
};

export async function createTicket(payload: TicketCreatePayload) {
  const response = await api.post("/tickets/", payload);
  return response.data;
}

export async function getTickets() {
  const response = await api.get("/tickets/");
  return response.data;
}
