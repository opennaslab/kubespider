enum MessageType {
  Notification = "notification",
  Download = "download",
}

interface Message<T = unknown> {
  type: MessageType;
  reciver?: number;
  payload: T;
}

interface Reply<T = unknown> {
  success: boolean;
  payload: T;
}

const SuccessReply = (payload?: unknown): Promise<Reply> =>
  new Promise((resolve) => {
    resolve({
      success: true,
      payload,
    });
  });

const ErrorReply = (payload?: unknown): Promise<Reply> =>
  new Promise((resolve) => {
    resolve({
      success: false,
      payload,
    });
  });

interface Listener {
  (payload: unknown): Promise<Reply>;
}

export type { Message, Reply, Listener };
export { MessageType, SuccessReply, ErrorReply };
