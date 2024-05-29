import Browser from "webextension-polyfill";

interface Config {
  server?: string;
  path?: string;
  token?: string;
  auth?: boolean;
  captureCookies?: boolean;
}

const defaultConfig: Config = {
  server: "",
  path: "",
  token: "",
  auth: false,
  captureCookies: false,
};

namespace Storage {
  export const read = async (): Promise<Config> => {
    return Browser.storage.local.get(defaultConfig).then((config) => {
      return config as Config;
    });
  };
  export const save = async (config: Config): Promise<void> => {
    return Browser.storage.local.set(config);
  };
}

export default Storage;
