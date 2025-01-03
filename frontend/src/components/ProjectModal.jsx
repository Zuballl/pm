import React, { useEffect, useState } from "react";

const ProjectModal = ({ active, handleModal, token, id, setErrorMessage }) => {
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [client, setClient] = useState("");
  const [deadline, setDeadline] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    const getProject = async () => {
      const requestOptions = {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
      };
      const response = await fetch(`/api/projects/${id}`, requestOptions);

      if (!response.ok) {
        setErrorMessage("Could not get the project");
      } else {
        const data = await response.json();
        setName(data.name);
        setDepartment(data.department);
        setClient(data.client);
        setDeadline(data.deadline);
        setDescription(data.description);
      }
    };

    if (id) {
      getProject();
    }
  }, [id, token]);

  const cleanFormData = () => {
    setName("");
    setDepartment("");
    setClient("");
    setDeadline("");
    setDescription("");
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        name: name,
        department: department,
        client: client,
        deadline: deadline,
        description: description,
      }),
    };
    const response = await fetch("/api/projects", requestOptions);
    if (!response.ok) {
      setErrorMessage("Something went wrong when creating project");
    } else {
      handleModal();
      cleanFormData();
    }
  };

  const handleUpdateProject = async (e) => {
    e.preventDefault();
    const requestOptions = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        name: name,
        department: department,
        client: client,
        deadline: deadline,
        description: description,
      }),
    };
    const response = await fetch(`/api/projects/${id}`, requestOptions);
    if (!response.ok) {
      setErrorMessage("Something went wrong when updating project");
    } else {
      handleModal();
      cleanFormData();
    }
  };

  return (
    <div className={`modal ${active && "is-active"}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-card">
        <header className="modal-card-head has-background-primary-light">
          <h1 className="modal-card-title">
            {id ? "Update Project" : "Create Project"}
          </h1>
        </header>
        <section className="modal-card-body">
          <form>
            <div className="field">
              <label className="label">Name</label>
              <div className="control">
                <input
                  type="text"
                  placeholder="Enter name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input"
                  required
                />
              </div>
            </div>
            <div className="field">
              <label className="label">Department</label>
              <div className="control">
                <input
                  type="text"
                  placeholder="Enter department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="input"
                  required
                />
              </div>
            </div>
            <div className="field">
              <label className="label">Client</label>
              <div className="control">
                <input
                  type="text"
                  placeholder="Enter client"
                  value={client}
                  onChange={(e) => setClient(e.target.value)}
                  className="input"
                />
              </div>
            </div>
            <div className="field">
              <label className="label">Deadline</label>
              <div className="control">
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="input"
                />
              </div>
            </div>
            <div className="field">
              <label className="label">Description</label>
              <div className="control">
                <textarea
                  placeholder="Enter description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="textarea"
                />
              </div>
            </div>
          </form>
        </section>
        <footer className="modal-card-foot has-background-primary-light">
          {id ? (
            <button className="button is-info" onClick={handleUpdateProject}>
              Update
            </button>
          ) : (
            <button className="button is-primary" onClick={handleCreateProject}>
              Create
            </button>
          )}
          <button className="button" onClick={handleModal}>
            Cancel
          </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectModal;