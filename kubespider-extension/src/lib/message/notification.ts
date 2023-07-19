import { sender, MessageType } from ".";

namespace Notification {
  export function success(
    reciver: number,
    title: string,
    content: string
  ): void {
    sender.sendMessage({
      type: MessageType.Notification,
      reciver: reciver,
      payload: {
        type: "success",
        title: title,
        content: content,
      },
    });
  }
  export function error(reciver: number, title: string, content: string): void {
    sender.sendMessage({
      type: MessageType.Notification,
      reciver: reciver,
      payload: {
        type: "error",
        title: title,
        content: content,
      },
    });
  }
}

export default Notification;
