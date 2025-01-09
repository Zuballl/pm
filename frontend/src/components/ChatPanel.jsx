import React, { useState, useEffect } from "react";
import { fetchGPTResponse, fetchChats, fetchProjects } from "../utils/api";
import ReactMarkdown from "react-markdown";

const ChatPanel = ({ token, userId }) => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [queryType, setQueryType] = useState("general");
  const [projectList, setProjectList] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");

  const loadChatHistory = async () => {
    try {
      const chats = await fetchChats(userId, token);
      setChatHistory(chats.chats);
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const loadProjects = async () => {
    try {
      const projects = await fetchProjects(userId, token);
      setProjectList(projects);
    } catch (error) {
      console.error("Failed to load projects:", error);
    }
  };

  useEffect(() => {
    if (token) {
      loadChatHistory();
      loadProjects();
    }
  }, [token]);

  const handleSendQuery = async () => {
    if (!query) return;
    try {
      const projectId = queryType === "project" ? selectedProject : null;
      const gptResponse = await fetchGPTResponse(userId, query, projectId, token);
      setResponse(typeof gptResponse === "string" ? gptResponse : JSON.stringify(gptResponse));
      setChatHistory([...chatHistory, { query, response: gptResponse }]);
      setQuery("");
    } catch (error) {
      console.error("Failed to fetch GPT response:", error);
    }
  };

  return (
    <div className="chat-panel">
      <h2 className="title has-text-centered">Chat with GPT</h2>
      <div className="chat-box">
        <div className="field">
          <label className="label">Query Type</label>
          <div className="control">
            <div className="select">
              <select
                value={queryType}
                onChange={(e) => setQueryType(e.target.value)}
              >
                <option value="general">General Query</option>
                <option value="project">Project-Specific Query</option>
              </select>
            </div>
          </div>
        </div>
        {queryType === "project" && (
          <div className="field">
            <label className="label">Select Project</label>
            <div className="control">
              <div className="select">
                <select
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                >
                  <option value="">--Select Project--</option>
                  {projectList.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
        <textarea
          placeholder="Ask something..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="textarea mb-4"
        />
        <button onClick={handleSendQuery} className="button is-primary is-fullwidth">
          Send
        </button>
      </div>
      <div className="response mt-5">
        <h3 className="title is-4 has-text-primary">GPT Response:</h3>
        <div className="box"
        style={{
            backgroundColor: "#2B2B2B",
            color: "#FFFFFF",
            borderRadius: "8px",
            padding: "16px",
            }}
        >
          <ReactMarkdown className="content">
            {typeof response === "string" ? response : JSON.stringify(response)}
          </ReactMarkdown>
        </div>
      </div>
      <div className="chat-history mt-5">
        <h3 className="title is-5">Past Chats</h3>
        <div className="box"style={{
            backgroundColor: "#2B2B2B",
            color: "#FFFFFF",
            borderRadius: "8px",
            padding: "16px",
            }}
        >
          {chatHistory.length === 0 ? (
            <p>No chat history available, start now!</p>
          ) : (
            <ul>
              {chatHistory.map((chat, index) => (
                <li key={index} className="mb-4">
                  <div className="box"
                  style={{
                    backgroundColor: "#2B2B2B",
                    color: "#FFFFFF",
                    borderRadius: "8px",
                    padding: "16px",
                    }}
                  >
                    <p className="has-text-weight-bold">
                      <strong>Q:</strong> {chat.query}
                    </p>
                    <ReactMarkdown className="content">
                      {typeof chat.response === "string" ? chat.response : JSON.stringify(chat.response)}
                    </ReactMarkdown>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;