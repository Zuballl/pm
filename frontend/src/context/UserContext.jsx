import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem("awesomeProjectManager") || null;
    } catch (err) {
      console.error("Error accessing localStorage:", err);
      return null;
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
      console.error("Error updating localStorage:", err);
    }
  }, [token]);

  return (
    <UserContext.Provider value={[token, setToken]}>
      {children}
    </UserContext.Provider>
  );
};