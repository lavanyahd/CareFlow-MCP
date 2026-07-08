import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ??
    "http://127.0.0.1:8000/api",

  headers: {
    "Content-Type": "application/json",
  },

  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,

  (error) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      "Unable to communicate with the server.";

    return Promise.reject(new Error(message));
  }
);

export default api;