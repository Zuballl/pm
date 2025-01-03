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