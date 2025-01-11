import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const fetchChats = async (userId, token) => {
  const response = await api.get(`/api/get-chats`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export const fetchGPTResponse = async (userId, query, projectId, token) => {
  const response = await api.post(
    "/api/gpt-query",
    {
      query,
      project_id: projectId,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data.response;
};

export const fetchProjects = async (userId, token) => {
  const response = await api.get(`/api/projects`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export default api;

export const connectClickUp = async (projectId, apiToken, listId, token) => {
  const response = await api.post(
    `/api/projects/${projectId}/clickup`,
    {
      api_token: apiToken,
      list_id: listId,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
};

// Slack API integrations
export const getSlackOAuthUrl = async (projectId, token) => {
  const response = await api.get(`/api/projects/${projectId}/slack/connect`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data.url;
};

export const handleSlackCallback = async (projectId, code, token) => {
  const response = await api.get(
    `/api/projects/${projectId}/slack/callback?code=${code}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
};

export const fetchSlackChannels = async (projectId, token) => {
  const response = await api.get(`/api/projects/${projectId}/slack/channels`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};