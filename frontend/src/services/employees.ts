import api from './api';

export const employeeService = {
  getAllEmployees: async () => {
    try {
      const response = await api.get('/employees/');
      return response; 
    } catch (error) {
      console.error('Error fetching employees:', error);
      throw error;
    }
  }
};