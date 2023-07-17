import { defineManifest } from "@crxjs/vite-plugin";
import pkg from "../package.json";

export default defineManifest({
  name: pkg.name,
  description: pkg.description,
  version: pkg.version,
  manifest_version: 3,
  icons: {
    "16": "img/icon16.png",
    "48": "img/icon48.png",
    "128": "img/icon128.png",
  },
  action: {
    default_popup: "popup.html",
    default_icon: "img/icon48.png",
  },
  background: {
    service_worker: "src/background/index.ts",
    type: "module",
  },
  content_scripts: [
    {
      matches: ["http://*/*", "https://*/*"],
      js: ["src/content/index.tsx"],
      run_at: "document_end",
    },
  ],
  web_accessible_resources: [
    {
      resources: ["img/icon16.png", "img/icon48.png", "img/icon128.png"],
      matches: ["http://*/*", "https://*/*"],
    },
  ],
  host_permissions: ["*://*/*"],
  permissions: [
    "storage",
    "declarativeNetRequest",
    "declarativeNetRequestFeedback",
    "contextMenus",
    "tabs",
    "cookies",
    "activeTab",
    "scripting",
  ],
});
