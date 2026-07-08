import api from "./api";

export interface LeaveRequest {
  id: number;
  employee_id: number;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
  reason: string | null;
}

export interface LeaveRequestCreate {
  employee_id: number;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string | null;
}

export const leaveService = {
  // Récupérer les congés (on filtre côté front pour le MVP)
  async getByEmployee(employeeId: number): Promise<LeaveRequest[]> {
    const response = await api.get<LeaveRequest[]>("/leave-requests");
    return response.data.filter(leave => leave.employee_id === employeeId);
  },

  // Créer une nouvelle demande
  async create(leaveData: LeaveRequestCreate): Promise<LeaveRequest> {
    const response = await api.post<LeaveRequest>("/leave-requests", leaveData);
    return response.data;
  },

  // Supprimer une demande
  async delete(id: number): Promise<void> {
    await api.delete(`/leave-requests/${id}`);
  }
};