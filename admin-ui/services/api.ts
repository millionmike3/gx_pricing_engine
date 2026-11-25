import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const authBaseURL = "/";

const apiBaseURL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://gxpricingengine-production.up.railway.app";

export const authApi = axios.create({
  baseURL: authBaseURL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export const api = axios.create({
  baseURL: apiBaseURL,
  withCredentials: false,
  headers: { "Content-Type": "application/json" },
});

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    if (
      error.response?.status !== 401 ||
      !original ||
      original._retry ||
      original.url?.includes("/auth/")
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = authApi
          .post("/auth/refresh", {})
          .then((response) => {
            const token = response.data?.accessToken;
            if (!token) throw new Error("Refresh response did not contain an access token.");
            setAccessToken(token);
            return token as string;
          })
          .catch(() => {
            setAccessToken(null);
            return null;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const token = await refreshPromise;
      if (!token) {
        if (typeof window !== "undefined") {
          window.location.assign("/login");
        }
        return Promise.reject(error);
      }

      original.headers = original.headers || {};
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch (refreshError) {
      setAccessToken(null);
      if (typeof window !== "undefined") {
        window.location.assign("/login");
      }
      return Promise.reject(refreshError);
    }
  }
);

