import {
  consumer,
  sender,
  MessageType,
  Reply,
  SuccessReply,
  ErrorReply,
} from "@message";
import Notification from "@message/notification";
import { api, downloadRequest } from "@api";
import Storage from "@storage";
import { Tab, Cookies } from "@bridge";
import Browser from "webextension-polyfill";

/**
 * create context menu
 */
Browser.runtime.onInstalled.addListener(() => {
  Browser.contextMenus.create({
    id: "KubespiderMenu",
    title: "Send to Kubespider",
    contexts: ["all"],
  });
});

/**
 * handle context menu click
 */
Browser.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "KubespiderMenu") {
    const tabId = tab?.id || (await Tab.getCurrentTabId());
    let dataSource = info.linkUrl;
    if (dataSource === "" || dataSource == null) {
      dataSource = tab?.url;
    }
    if (dataSource === "" || dataSource == null) {
      return;
    }
    const { server, token, captureCookies } = await Storage.read();
    if (!server || server === "") {
      Notification.error(
        tabId,
        "Kubespider",
        "Please set server address first!"
      );
      return;
    }
    const cookies = captureCookies
      ? await Cookies.getAll(dataSource)
      : undefined;
    const response = await api(
      downloadRequest(server, dataSource, undefined, cookies, token)
    );
    if (response.status === 200) {
      Notification.success(
        tabId,
        "Kubespider",
        `${dataSource} download success`
      );
    } else {
      Notification.error(tabId, "Kubespider", `${response.body}`);
    }
  }
});

/**
 * handle download request
 */
consumer.addListener(MessageType.Download, async (payload): Promise<Reply> => {
  const { dataSource, path } = payload as {
    dataSource: string;
    path?: string;
  };
  const { server, token, captureCookies } = await Storage.read();
  if (!server || server === "") {
    return ErrorReply("Please set server address first");
  }
  const tabId = await Tab.getCurrentTabId();
  const cookies = captureCookies ? await Cookies.getAll(dataSource) : undefined;

  const response = await api(
    downloadRequest(server, dataSource, path, cookies, token)
  );
  if (response.status === 200) {
    Notification.success(tabId, "Kubespider", `${dataSource} download success`);
    return SuccessReply();
  } else {
    Notification.error(tabId, "Kubespider", `${response.body}`);
    return ErrorReply();
  }
});

// ========== listen to messages from content&popup ==========
consumer.addListener(
  MessageType.Notification,
  async (payload): Promise<Reply> => {
    // notification resend to content
    let { tabId } = payload as { tabId?: number };
    if (tabId) {
      return SuccessReply();
    }
    tabId = await Tab.getCurrentTabId();
    if (tabId === -1) {
      return ErrorReply("No active tab");
    }
    return sender.sendMessage({
      type: MessageType.Notification,
      reciver: tabId,
      payload,
    });
  }
);
