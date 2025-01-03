import React from "react";

const ErrorMessage = ({ message }) => (
  <p className="has-text-weight-bold has-text-danger">
    {typeof message === 'string' ? message : 'An error occurred'}
  </p>
);

export default ErrorMessage;