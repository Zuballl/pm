import React, { useContext, useEffect, useState } from "react";

import Register from "./components/Register";
import Login from "./components/Login";
import Header from "./components/Header";
import Table from "./components/Table";
import ChatPanel from "./components/ChatPanel";
import { UserContext } from "./context/UserContext";

const App = () => {
  const [message, setMessage] = useState("");
  const [token, setToken] = useContext(UserContext);
  const [userId, setUserId] = useState(null); // To store the user's ID
  const [username, setUsername] = useState(""); // To store the user's username

  const getWelcomeMessage = async () => {
    const requestOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };
    const response = await fetch("/api", requestOptions);
    const data = await response.json();

    if (!response.ok) {
      console.log("Something went wrong");
    } else {
      setMessage(data.message);
    }
  };

  const fetchUserDetails = async () => {
    const requestOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    };
    const response = await fetch("/api/users/me", requestOptions);
    const data = await response.json();

    if (!response.ok) {
      console.log("Error fetching user details");
    } else {
      setUserId(data.id);
      setUsername(data.username);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUserId(null);
    setUsername("");
  };

  useEffect(() => {
    getWelcomeMessage();
    if (token) {
      fetchUserDetails();
    }
  }, [token]);

  return (
    <>
      <Header title={message} />
      {token && (
        <div className="user-info">
          <div className="container has-text-centered mt-4">
            <p>
              Logged in as <strong>{username}</strong>
            </p>
            <button className="button is-danger is-small mt-2" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      )}
      <div className="columns">
        <div className="column"></div>
        <div className="column m-5 is-two-thirds">
          {!token ? (
            <div className="columns">
              <Register /> <Login />
            </div>
          ) : (
            <>
              <Table token={token} />
              <ChatPanel token={token} userId={userId} />
            </>
          )}
        </div>
        <div className="column"></div>
      </div>
    </>
  );
};

export default App;