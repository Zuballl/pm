import React, { useState } from "react";
import { connectClickUp } from "../../utils/api";

const ClickUpModal = ({ active, handleModal, projectId, setErrorMessage, token }) => {
  const [clickUpToken, setClickUpToken] = useState("");
  const [clickUpListId, setClickUpListId] = useState("");

  const handleConnect = async (e) => {
    e.preventDefault();

    try {
      await connectClickUp(projectId, clickUpToken, clickUpListId, token);
      handleModal(); // Close the modal on success
    } catch (error) {
      console.error("Failed to connect to ClickUp:", error);
      setErrorMessage("Failed to connect to ClickUp. Please check your credentials.");
    }
  };

  return (
    <div className={`modal ${active ? "is-active" : ""}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-card">
        <header className="modal-card-head">
          <p className="modal-card-title">Connect to ClickUp</p>
        </header>
        <section className="modal-card-body">
          <div className="field">
            <label className="label">ClickUp Token</label>
            <div className="control">
              <input
                className="input"
                type="text"
                placeholder="Enter your ClickUp token"
                value={clickUpToken}
                onChange={(e) => setClickUpToken(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="field">
            <label className="label">ClickUp List ID</label>
            <div className="control">
              <input
                className="input"
                type="text"
                placeholder="Enter the ClickUp list ID"
                value={clickUpListId}
                onChange={(e) => setClickUpListId(e.target.value)}
                required
              />
            </div>
          </div>
        </section>
        <footer className="modal-card-foot">
          <button className="button is-primary" onClick={handleConnect}>
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

export default ClickUpModal;