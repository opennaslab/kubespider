import Browser from "webextension-polyfill";
import type { Message, Reply } from "./types";

class Sender {
  sendMessage(message: Message): Promise<Reply> {
    if (message.reciver && message.reciver > 0) {
      return Browser.tabs.sendMessage(message.reciver, message);
    } else {
      return Browser.runtime.sendMessage(message);
    }
  }
}

export { Sender };
