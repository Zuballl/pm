import React from "react";

const Header = ({ title }) => {
  return (
    <header className="has-text-centered p-4">
      <h1 className="title">{title}</h1>
    </header>
  );
};

export default Header;