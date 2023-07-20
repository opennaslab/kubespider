import { MessageType, Reply, SuccessReply, consumer } from "@message";
import { Alert } from "@component/Alert";
import { useEffect, useState } from "react";
import { useEvent } from "@polyfill";
import { uuidv4 } from "../util";

interface MessageData {
  id?: string;
  title: string;
  content: string;
  type?: "success" | "error";
  delay?: number;
}

function Overlay() {
  const [messages, setMessages] = useState([] as MessageData[]);

  const onMessage = useEvent((message: MessageData) => {
    setMessages([...messages.filter((m) => m.id !== message.id), message]);
  });

  const removeMessage = useEvent((id: string) => {
    setMessages(messages.filter((message) => message.id !== id));
  });

  useEffect(() => {
    consumer.addListener(
      MessageType.Notification,
      (payload): Promise<Reply> => {
        const { id, title, content, type, delay } = payload as MessageData;
        const messageId = id || uuidv4();
        const delayTime = delay || 4500;
        // render message
        onMessage({ id: messageId, title, content, type, delay });
        // remove message
        if (delayTime > 0) {
          setTimeout(() => {
            removeMessage(messageId);
          }, delayTime);
        }
        // return message id
        return new Promise((resolve) => {
          resolve(
            SuccessReply({
              messageId,
            })
          );
        });
      }
    );
  }, []);

  return (
    <div className="box-content h-auto w-1/5 mt-20 mr-4 flex flex-col space-y-4 fixed z-max top-0 right-0">
      {messages.map((message) => (
        <Alert
          key={message.id}
          title={message.title}
          content={message.content}
          type={message.type}
        />
      ))}
    </div>
  );
}

export default Overlay;
