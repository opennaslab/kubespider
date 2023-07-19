import React from "react";
import ReactDOM from "react-dom/client";
import styles from "./index.css?inline";
import Overlay from "./Overlay";

function initContainer() {
  // query or create container
  let container = document.getElementById("kubespider-extension-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "kubespider-extension-container";
    // inject container to body
    document.body.appendChild(container);
  }
  // create shadow dom
  let shadowContainer = container.shadowRoot;
  if (!shadowContainer) {
    shadowContainer = container.attachShadow({ mode: "closed" });
  }
  let shadowWrapper = shadowContainer.getElementById("app");
  if (!shadowWrapper) {
    shadowWrapper = document.createElement("div");
    shadowWrapper.id = "app";
    shadowContainer.appendChild(shadowWrapper);
  }
  return shadowWrapper;
}

function mount(container: HTMLElement) {
  ReactDOM.createRoot(container).render(
    <React.StrictMode>
      <style>{styles}</style>
      <Overlay />
    </React.StrictMode>
  );
}

export function onExecute() {
  console.log("[kubespider-extension] content script injected");
  const container = initContainer();
  mount(container);
}
