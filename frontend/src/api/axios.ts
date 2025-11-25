import axios from "axios";
import { useUserStore } from "@/stores/userStore";
import router from "@/router"; // si exportas "export default router"

const api = axios.create({
  baseURL: "http://127.0.0.1:5000",
});

// === REQUEST INTERCEPTOR ===
// Adjunta el token automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// === RESPONSE INTERCEPTOR ===
// Maneja expiración del token (401)
api.interceptors.response.use(
  (response) => response,

  (error) => {
    const userStore = useUserStore();

    // Si el backend responde 401 => token inválido o expirado
    if (error.response?.status === 401) {
      userStore.logout();         // limpia token
      router.push("/login");      // redirige al login
    }

    return Promise.reject(error);
  }
);

export default api;
