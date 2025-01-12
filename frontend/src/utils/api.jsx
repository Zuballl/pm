import axios from "axios";

// Create an Axios instance for API calls
const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // Replace with the actual base URL
});

// Helper function to get default headers with Authorization
const getAuthHeaders = (token) => ({
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

// Generic error handler
const handleApiError = (error) => {
  console.error("API Error:", error.response?.data || error.message);
  throw new Error(error.response?.data?.detail || "An error occurred during the API call");
};

// Fetch chat history
export const fetchChats = async (userId, token) => {
  try {
    const response = await api.get(`/api/get-chats`, getAuthHeaders(token));
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Fetch GPT response
export const fetchGPTResponse = async (userId, query, projectId, token) => {
  try {
    const response = await api.post(
      "/api/gpt-query",
      {
        query,
        project_id: projectId,
      },
      getAuthHeaders(token)
    );
    return response.data.response;
  } catch (error) {
    handleApiError(error);
  }
};

// Fetch projects
export const fetchProjects = async (userId, token) => {
  try {
    const response = await api.get(`/api/projects`, getAuthHeaders(token));
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Connect to ClickUp
export const connectClickUp = async (projectId, apiToken, listId, token) => {
  try {
    const response = await api.post(
      `/api/projects/${projectId}/clickup`,
      {
        api_token: apiToken,
        list_id: listId,
      },
      getAuthHeaders(token)
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Configure Slack for a project
export const configureSlack = async (projectId, config, token) => {
  try {
    const response = await api.post(
      `/api/projects/${projectId}/slack/config`,
      config,
      getAuthHeaders(token)
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// Get Slack OAuth URL
export const getSlackOAuthUrl = async (projectId, token) => {
  try {
    const response = await api.get(
      `/api/projects/${projectId}/slack/connect`,
      getAuthHeaders(token)
    );
    return response.data.url;
  } catch (error) {
    handleApiError(error);
  }
};

// Handle Slack OAuth callback
export const handleSlackCallback = async (projectId, code, token) => {
  try {
    const response = await api.get(
      `/api/projects/${projectId}/slack/callback?code=${code}`,
      getAuthHeaders(token)
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export default api;