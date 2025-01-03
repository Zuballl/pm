import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext();

export const UserProvider = (props) => {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem("awesomeProjectManager") || null;
    } catch (err) {
      console.error("LocalStorage is not accessible:", err);
      return null; // Fallback if localStorage is not accessible
    }
  });

  useEffect(() => {
    try {
      if (token) {
        localStorage.setItem("awesomeProjectManager", token);
      } else {
        localStorage.removeItem("awesomeProjectManager");
      }
    } catch (err) {
      console.error("Failed to update localStorage:", err);
    }
  }, [token]);

  return (
    <UserContext.Provider value={[token, setToken]}>
      {props.children}
    </UserContext.Provider>
  );
};