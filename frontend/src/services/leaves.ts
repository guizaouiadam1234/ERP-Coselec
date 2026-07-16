import api from "./api";

export interface LeaveRequest {
  id: number;
  employee_id: number;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
  reason: string | null;
  pdf_url: string | null;
  justificatif_url: string | null;
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
  },

  // Télécharger l'attestation
  async downloadCertificate(id: number): Promise<void> {
    const response = await api.get<Blob>(
      `/leave-requests/${id}/certificate`,
      { responseType: 'blob' }
    );
    
    // Essayer de lire le nom du fichier depuis les headers, sinon fallback générique
    let fileName = `conge_${id}.pdf`;
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        fileName = match[1];
      }
    }

    const url = window.URL.createObjectURL(response.data);
    const link = window.document.createElement('a');
    link.href = url;
    link.download = fileName;
    window.document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};