import { Consumer } from "./consumer";
import { Sender } from "./sender";
import { MessageType, SuccessReply, ErrorReply } from "./types";
import { Reply } from "./types";

const consumer = new Consumer();
const sender = new Sender();

export { sender, consumer, MessageType, SuccessReply, ErrorReply };
export type { Reply };
