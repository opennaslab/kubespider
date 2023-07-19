interface Request<T = unknown> {
  url: string;
  method: "POST" | "GET";
  headers: Map<string, string>;
  body?: T;
}

interface Response<T = string> {
  status: number;
  body: T;
}

const downloadRequest = (
  server: string,
  dataSource: string,
  path?: string,
  cookies?: string,
  token?: string
): Request<{
  dataSource: string;
  path?: string;
  cookies?: string;
}> => {
  const headers = new Map<string, string>();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return {
    url: `${server}/api/v1/download`,
    method: "POST",
    headers: headers,
    body: {
      dataSource,
      path,
      cookies,
    },
  };
};

const healthzRequest = (server: string): Request => {
  return {
    url: `${server}/healthz`,
    method: "GET",
    headers: new Map(),
  };
};

const refreshRequest = (server: string, token?: string): Request => {
  const headers = new Map<string, string>();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return {
    url: `${server}/api/v1/refresh`,
    method: "GET",
    headers: headers,
  };
};

export { downloadRequest, healthzRequest, refreshRequest };
export type { Request, Response };
