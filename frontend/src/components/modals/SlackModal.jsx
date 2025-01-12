import React, { useState } from "react";
import { configureSlack, getSlackOAuthUrl } from "../../utils/api";

const SlackModal = ({ active, handleModal, projectId, token, setErrorMessage }) => {
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const [redirectUri, setRedirectUri] = useState("");

  // Step 1: Save Slack configuration
  const saveSlackConfig = async () => {
    try {
      const config = { client_id: clientId, client_secret: clientSecret, redirect_uri: redirectUri };
      await configureSlack(projectId, config, token);
      const oauthUrl = await getSlackOAuthUrl(projectId, token);
      window.location.href = oauthUrl; // Redirect to Slack OAuth
    } catch (error) {
      setErrorMessage("Failed to configure Slack integration");
    }
  };

  return (
    <div className={`modal ${active ? "is-active" : ""}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-card">
        <header className="modal-card-head">
          <p className="modal-card-title">Connect Slack</p>
          <button className="delete" aria-label="close" onClick={handleModal}></button>
        </header>
        <section className="modal-card-body">
          <div className="field">
            <label className="label">Client ID</label>
            <div className="control">
              <input
                className="input"
                type="text"
                placeholder="Enter Client ID"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
              />
            </div>
          </div>
          <div className="field">
            <label className="label">Client Secret</label>
            <div className="control">
              <input
                className="input"
                type="text"
                placeholder="Enter Client Secret"
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
              />
            </div>
          </div>
          <div className="field">
            <label className="label">Redirect URI</label>
            <div className="control">
              <input
                className="input"
                type="text"
                placeholder="Enter Redirect URI"
                value={redirectUri}
                onChange={(e) => setRedirectUri(e.target.value)}
              />
            </div>
          </div>
        </section>
        <footer className="modal-card-foot">
          <button className="button is-primary" onClick={saveSlackConfig}>
            Connect
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