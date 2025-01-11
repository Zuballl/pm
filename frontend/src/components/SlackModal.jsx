import React from "react";
import { getSlackOAuthUrl } from "../utils/api";

const SlackModal = ({ active, handleModal, projectId, token, setErrorMessage }) => {
  const initiateSlackOAuth = async () => {
    try {
      const url = await getSlackOAuthUrl(projectId, token);
      window.location.href = url; // Redirect to Slack OAuth
    } catch (error) {
      setErrorMessage("Failed to generate Slack OAuth URL");
    }
  };

  return (
    <div className={`modal ${active && "is-active"}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-card">
        <header className="modal-card-head has-background-primary-light">
          <h1 className="modal-card-title">Connect to Slack</h1>
        </header>
        <section className="modal-card-body">
          <p>Click the button below to connect this project to Slack.</p>
        </section>
        <footer className="modal-card-foot has-background-primary-light">
          <button className="button is-primary" onClick={initiateSlackOAuth}>
            Connect to Slack
          </button>
          <button className="button" onClick={handleModal}>
            Cancel
          </button>
        </footer>
      </div>
    </div>
  );
};

export default SlackModal;