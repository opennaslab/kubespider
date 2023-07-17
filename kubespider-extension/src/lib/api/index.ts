import type { Request, Response } from "./types";
import { healthzRequest, downloadRequest, refreshRequest } from "./types";

async function api(request: Request): Promise<Response> {
  const requestInit: RequestInit = {
    method: request.method,
  };
  // prepare headers
  const headers: HeadersInit = {};
  if (request.headers.size > 0) {
    for (const [key, value] of request.headers) {
      headers[key] = value;
    }
    requestInit.headers = headers;
  }
  if (request.method === "POST") {
    requestInit.body = JSON.stringify(request.body);
  }

  return fetch(request.url, requestInit)
    .then((response) => {
      return response.text().then((body) => {
        return {
          status: response.status,
          body: body,
        };
      });
    })
    .catch((error) => {
      return {
        status: 500,
        body: error,
      };
    });
}

export { api, healthzRequest, downloadRequest, refreshRequest };
