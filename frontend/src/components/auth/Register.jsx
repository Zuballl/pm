import React, { useContext, useState } from "react";
import { UserContext } from "../../context/UserContext";
import ErrorMessage from "../common/ErrorMessage";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmationPassword, setConfirmationPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [, setToken] = useContext(UserContext);

  // Function to handle the registration process
  const submitRegistration = async () => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, hashed_password: password }),
    };

    try {
      const response = await fetch("/api/users", requestOptions);
      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || "Registration failed");
      } else {
        // Set the token in UserContext and localStorage
        setToken(data.access_token);
        localStorage.setItem("awesomeProjectManager", data.access_token);
        setErrorMessage(""); // Clear any previous error messages
      }
    } catch (error) {
      setErrorMessage("An error occurred while registering. Please try again.");
    }
  };

  // Function to handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (password === confirmationPassword && password.length > 5) {
      submitRegistration();
    } else {
      setErrorMessage(
        "Passwords must match and be greater than 5 characters."
      );
    }
  };

  return (
    <div className="column">
      <form className="box" onSubmit={handleSubmit} noValidate>
        <h1 className="title has-text-centered">Register</h1>
        <div className="field">
          <label className="label">Username</label>
          <div className="control">
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
              required
              autoComplete="username"
            />
          </div>
        </div>
        <div className="field">
          <label className="label">Password</label>
          <div className="control">
            <input
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              required
              autoComplete="new-password"
            />
          </div>
        </div>
        <div className="field">
          <label className="label">Confirm Password</label>
          <div className="control">
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmationPassword}
              onChange={(e) => setConfirmationPassword(e.target.value)}
              className="input"
              required
              autoComplete="new-password"
            />
          </div>
        </div>
        {/* Error Message */}
        <ErrorMessage message={errorMessage} />
        <br />
        <button className="button is-primary" type="submit">
          Register
        </button>
      </form>
    </div>
  );
};

export default Register;