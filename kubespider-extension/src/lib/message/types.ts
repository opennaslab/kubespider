enum MessageType {
  Notification = "notification",
  Download = "download",
}

interface Message<T = unknown> {
  type: MessageType;
  reciver?: number;
  payload: T;
}

interface Reply {
  success: boolean;
  message?: string;
}

const SuccessReply = (message?: string): Promise<Reply> =>
  new Promise((resolve) => {
    resolve({
      success: true,
      message,
    });
  });

const ErrorReply = (message?: string): Promise<Reply> =>
  new Promise((resolve) => {
    resolve({
      success: false,
      message,
    });
  });

interface Listener {
  (payload: unknown): Promise<Reply>;
}

export type { Message, Reply, Listener };
export { MessageType, SuccessReply, ErrorReply };
