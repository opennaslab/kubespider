import { sender, MessageType, Reply } from ".";

interface NotificationPayload {
  id?: number;
  title: string;
  content: string;
  delay?: number;
}

namespace Notification {
  export function success(
    reciver: number,
    payload: NotificationPayload
  ): Promise<Reply> {
    return sender.sendMessage({
      type: MessageType.Notification,
      reciver: reciver,
      payload: {
        type: "success",
        ...payload,
      },
    });
  }

  export function error(
    reciver: number,
    payload: NotificationPayload
  ): Promise<Reply> {
    return sender.sendMessage({
      type: MessageType.Notification,
      reciver: reciver,
      payload: {
        type: "error",
        ...payload,
      },
    });
  }

  export function info(
    reciver: number,
    payload: NotificationPayload
  ): Promise<Reply> {
    return sender.sendMessage({
      type: MessageType.Notification,
      reciver: reciver,
      payload: {
        type: "info",
        ...payload,
      },
    });
  }
}

export default Notification;
