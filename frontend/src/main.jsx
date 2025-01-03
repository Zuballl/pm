import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bulma/css/bulma.min.css';
import App from './App';
import { UserProvider } from './context/UserContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UserProvider>
      <App />
    </UserProvider>
  </React.StrictMode>
);