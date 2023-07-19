import browser from "webextension-polyfill";
import type { Message, Listener, MessageType, Reply } from "./types";
import { ErrorReply } from "./types";

const topics: Map<string, Listener> = new Map();

function dispatchEvent(message: Message): Promise<Reply> {
  const { type, payload } = message;
  let listener;
  if (topics.has(type)) {
    listener = topics.get(type);
  }
  if (!listener) {
    return ErrorReply(`No listener for message type: ${type}`);
  }

  return listener(payload);
}

class Consumer {
  constructor() {
    browser.runtime.onMessage.addListener((message) => {
      return dispatchEvent(message);
    });
  }
  addListener(type: MessageType, callback: Listener) {
    if (topics.has(type)) {
      console.warn(`[kubespider] listener for ${type} already exists`);
    }
    topics.set(type, callback);
  }
}

export { Consumer };
