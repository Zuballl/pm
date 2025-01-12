import React, { useState, useEffect } from "react";
import { fetchGPTResponse, fetchChats, fetchProjects } from "../../utils/api";
import ReactMarkdown from "react-markdown";

const ChatPanel = ({ token, userId }) => {
  const [query, setQuery] = useState("");
  const [chatState, setChatState] = useState({
    response: "",
    chatHistory: [],
  });
  const [queryType, setQueryType] = useState("general");
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");

  const { response, chatHistory } = chatState;

  const handleApiErrors = (error, message) => {
    console.error(message, error);
  };

  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const chats = await fetchChats(userId, token);
        setChatState((prevState) => ({
          ...prevState,
          chatHistory: chats.chats,
        }));
      } catch (error) {
        handleApiErrors(error, "Failed to load chat history");
      }
    };

    const loadProjects = async () => {
      try {
        const projects = await fetchProjects(userId, token);
        setProjects(projects);
      } catch (error) {
        handleApiErrors(error, "Failed to load projects");
      }
    };

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

      setChatState((prevState) => ({
        ...prevState,
        chatHistory: [
          ...prevState.chatHistory,
          { query, response: gptResponse },
        ],
        response: gptResponse,
      }));

      setQuery("");
    } catch (error) {
      handleApiErrors(error, "Failed to fetch GPT response");
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
                  {projects.map((project) => (
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
        <button
          onClick={handleSendQuery}
          className="button is-primary is-fullwidth"
        >
          Send
        </button>
      </div>
      <div className="response mt-5">
        <h3 className="title is-4 has-text-primary">GPT Response:</h3>
        <div className="box">
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      </div>
      <div className="chat-history mt-5">
        <h3 className="title is-5">Past Chats</h3>
        <div className="box">
          {chatHistory.length === 0 ? (
            <p>No chat history available. Start chatting!</p>
          ) : (
            <ul>
              {chatHistory.map((chat, index) => (
                <li key={index}>
                  <div className="box">
                    <p>
                      <strong>Q:</strong> {chat.query}
                    </p>
                    <ReactMarkdown>{chat.response}</ReactMarkdown>
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