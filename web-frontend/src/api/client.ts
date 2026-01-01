import axios from "axios";

const API_URL = "http://localhost:8000/api";

const client = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// a request interceptor to attach the JWT token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("Attached Token:", token.substring(0, 10) + "..."); // [DEBUG]
    } else {
      console.warn("No access token found in localStorage");
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Optional: Add response interceptor for 401 (Token Expired) handling
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      // Token likely expired.
      // TODO: Implement refresh token logic here if needed.
      // For now, logout user.
      // localStorage.removeItem('access_token');
      // window.location.href = '/login';
    }

    return Promise.reject(error);
  },
);

export default client;
