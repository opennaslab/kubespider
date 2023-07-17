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
    setMessages([...messages, message]);
  });

  useEffect(() => {
    consumer.addListener(
      MessageType.Notification,
      (payload): Promise<Reply> => {
        const { title, content, type, delay } = payload as MessageData;
        onMessage({ id: uuidv4(), title, content, type, delay });
        return new Promise((resolve) => {
          resolve(SuccessReply());
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
          delay={message.delay}
        />
      ))}
    </div>
  );
}

export default Overlay;
