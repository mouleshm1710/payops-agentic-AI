import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const askAgent = async (payload) => {
  const response = await axios.post(`${API_BASE_URL}/agent/ask`, payload);
  return response.data;
};

export const getPayrollExceptions = async () => {
  const response = await axios.get(`${API_BASE_URL}/analytics/payroll-exceptions`);
  return response.data;
};

export const getOvertimeTrends = async () => {
  const response = await axios.get(`${API_BASE_URL}/analytics/overtime-trends`);
  return response.data;
};

export const getTicketStatus = async () => {
  const response = await axios.get(`${API_BASE_URL}/analytics/ticket-status`);
  return response.data;
};

export const getDeductionSummary = async () => {
  const response = await axios.get(`${API_BASE_URL}/analytics/deduction-summary`);
  return response.data;
};

export const getHighRiskRecords = async () => {
  const response = await axios.get(
    `${API_BASE_URL}/analytics/high-risk-records`
  );
  return response.data;
};