import React, { useEffect, useState } from "react";

const ProjectModal = ({ active, handleModal, token, id, setErrorMessage }) => {
  const [formData, setFormData] = useState({
    name: "",
    department: "",
    client: "",
    deadline: "",
    description: "",
  });

  const { name, department, client, deadline, description } = formData;

  useEffect(() => {
    const getProject = async () => {
      try {
        const response = await fetch(`/api/projects/${id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) throw new Error("Could not get the project");
        const data = await response.json();
        setFormData(data);
      } catch (err) {
        setErrorMessage(err.message);
      }
    };

    if (id) getProject();
  }, [id, token]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e, method) => {
    e.preventDefault();
    try {
      const endpoint = id ? `/api/projects/${id}` : "/api/projects";
      const response = await fetch(endpoint, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error(`Failed to ${id ? "update" : "create"} project`);
      handleModal();
      setFormData({ name: "", department: "", client: "", deadline: "", description: "" });
    } catch (err) {
      setErrorMessage(err.message);
    }
  };

  return (
    <div className={`modal ${active ? "is-active" : ""}`}>
      <div className="modal-background" onClick={handleModal}></div>
      <div className="modal-card">
        <header className="modal-card-head">
          <p className="modal-card-title">{id ? "Update Project" : "Create Project"}</p>
        </header>
        <section className="modal-card-body">
          <form>
            {["name", "department", "client", "deadline"].map((field) => (
              <div className="field" key={field}>
                <label className="label">{field.charAt(0).toUpperCase() + field.slice(1)}</label>
                <div className="control">
                  <input
                    type={field === "deadline" ? "date" : "text"}
                    name={field}
                    placeholder={`Enter ${field}`}
                    value={formData[field]}
                    onChange={handleChange}
                    className="input"
                    required={field !== "client"}
                  />
                </div>
              </div>
            ))}
            <div className="field">
              <label className="label">Description</label>
              <div className="control">
                <textarea
                  name="description"
                  placeholder="Enter description"
                  value={description}
                  onChange={handleChange}
                  className="textarea"
                />
              </div>
            </div>
          </form>
        </section>
        <footer className="modal-card-foot">
          <button
            className="button is-primary"
            onClick={(e) => handleSubmit(e, id ? "PUT" : "POST")}
          >
            {id ? "Update" : "Create"}
          </button>
          <button className="button" onClick={handleModal}>
            Cancel
          </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectModal;