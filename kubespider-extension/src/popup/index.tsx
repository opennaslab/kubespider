import React from "react";
import ReactDOM from "react-dom/client";
import App from "./Popup";
import styles from "./index.css?inline";

ReactDOM.createRoot(document.getElementById("app") as HTMLElement).render(
  <React.StrictMode>
    <style>{styles}</style>
    <App />
  </React.StrictMode>
);
