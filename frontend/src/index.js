import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Create root element (React 18+)
const root = ReactDOM.createRoot(document.getElementById("root"));

// Render App
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);