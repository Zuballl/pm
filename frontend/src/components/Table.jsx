import React, { useContext, useEffect, useState } from "react";
import { format } from "date-fns";

import ErrorMessage from "./ErrorMessage";
import ProjectModal from "./ProjectModal";
import ClickUpModal from "./ClickUpModal"; 
import SlackModal from "./SlackModal"; // New Modal Component
import { UserContext } from "../context/UserContext";

const Table = () => {
  const [token] = useContext(UserContext);
  const [projects, setProjects] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [activeModal, setActiveModal] = useState(false);
  const [activeClickUpModal, setActiveClickUpModal] = useState(false);
  const [activeSlackModal, setActiveSlackModal] = useState(false); // State for Slack Modal
  const [id, setId] = useState(null);

  const handleUpdate = async (id) => {
    setId(id);
    setActiveModal(true);
  };

  const handleConnectClickUp = async (id) => {
    setId(id);
    setActiveClickUpModal(true);
  };

  const handleConnectSlack = async (id) => {
    setId(id);
    setActiveSlackModal(true);
  };

  const handleDelete = async (id) => {
    const requestOptions = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    };
    const response = await fetch(`/api/projects/${id}`, requestOptions);
    if (!response.ok) {
      setErrorMessage("Failed to delete project");
    }

    getProjects();
  };

  const getProjects = async () => {
    const requestOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    };
    const response = await fetch("/api/projects", requestOptions);
    if (!response.ok) {
      setErrorMessage("Something went wrong. Couldn't load the projects");
    } else {
      const data = await response.json();
      setProjects(data);
      setLoaded(true);
    }
  };

  useEffect(() => {
    getProjects();
  }, []);

  const handleModal = () => {
    setActiveModal(!activeModal);
    getProjects();
    setId(null);
  };

  const handleClickUpModal = () => {
    setActiveClickUpModal(!activeClickUpModal);
    getProjects();
    setId(null);
  };

  const handleSlackModal = () => {
    setActiveSlackModal(!activeSlackModal);
    getProjects();
    setId(null);
  };

  return (
    <>
      <ProjectModal
        active={activeModal}
        handleModal={handleModal}
        token={token}
        id={id}
        setErrorMessage={setErrorMessage}
      />
      <ClickUpModal
        active={activeClickUpModal}
        handleModal={handleClickUpModal}
        token={token}
        projectId={id}
        setErrorMessage={setErrorMessage}
      />
      <SlackModal
        active={activeSlackModal}
        handleModal={handleSlackModal}
        token={token}
        projectId={id}
        setErrorMessage={setErrorMessage}
      />
      <button
        className="button is-fullwidth mb-5 is-primary"
        onClick={() => setActiveModal(true)}
      >
        Create New Project
      </button>
      <ErrorMessage message={errorMessage} />
      {loaded && projects ? (
        <table className="table is-fullwidth">
          <thead>
            <tr>
              <th>Name</th>
              <th>Department</th>
              <th>Client</th>
              <th>Deadline</th>
              <th>Description</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id}>
                <td>{project.name}</td>
                <td>{project.department}</td>
                <td>{project.client}</td>
                <td>{project.deadline}</td>
                <td>{project.description}</td>
                <td>{format(new Date(project.date_last_updated), "MMM do yyyy")}</td>
                <td>
                  <button
                    className="button mr-2 is-info is-light"
                    onClick={() => handleUpdate(project.id)}
                  >
                    Update
                  </button>
                  <button
                    className="button mr-2 is-primary is-light"
                    onClick={() => handleConnectClickUp(project.id)}
                  >
                    Connect ClickUp
                  </button>
                  <button
                    className="button mr-2 is-warning is-light"
                    onClick={() => handleConnectSlack(project.id)}
                  >
                    Connect Slack
                  </button>
                  <button
                    className="button mr-2 is-danger is-light"
                    onClick={() => handleDelete(project.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Loading</p>
      )}
    </>
  );
};

export default Table;