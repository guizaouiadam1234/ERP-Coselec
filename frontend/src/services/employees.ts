import api from './api';
export const  getEmployees = async () => {
  try {
    const response = await api.get('/employees/');
    return response.data;
  } catch (error) {
    console.error('Error fetching employees:', error);
    throw error;
  }
};