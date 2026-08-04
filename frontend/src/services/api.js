import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==========================================
// TICKETS
// ==========================================

export const getTickets = async (limit = 10) => {
  try {
    const response = await api.get(`/tickets?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Erreur getTickets:', error);
    throw error;
  }
};

export const getTicket = async (ticketId) => {
  try {
    const response = await api.get(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Erreur getTicket:', error);
    throw error;
  }
};

export const processTicket = async (ticketId) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/process`);
    return response.data;
  } catch (error) {
    console.error('Erreur processTicket:', error);
    throw error;
  }
};

export const replyToTicket = async (ticketId, content) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/reply`, { content });
    return response.data;
  } catch (error) {
    console.error('Erreur replyToTicket:', error);
    throw error;
  }
};

export const processAllTickets = async (ticketIds) => {
  try {
    const results = await Promise.all(
      ticketIds.map(id => processTicket(id))
    );
    return results;
  } catch (error) {
    console.error('Erreur processAllTickets:', error);
    throw error;
  }
};

// ==========================================
// STATS
// ==========================================

export const getStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Erreur getStats:', error);
    throw error;
  }
};

// ==========================================
// AGENT
// ==========================================

export const getAgentStatus = async () => {
  try {
    const response = await api.get('/agent/status');
    return response.data;
  } catch (error) {
    console.error('Erreur getAgentStatus:', error);
    throw error;
  }
};

export default api;