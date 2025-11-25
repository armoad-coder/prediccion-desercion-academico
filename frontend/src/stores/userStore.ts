import { defineStore } from "pinia";
import api from "@/api/axios";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
    loading: false,
  }),

  actions: {
    async login(username: string, password: string) {
      this.loading = true;
      try {
        const { data } = await api.post("/auth/login", { username, password });

        this.token = data.access_token;
        localStorage.setItem("token", data.access_token);

        await this.getProfile();

        return true;
      } catch (error) {
        return false;
      } finally {
        this.loading = false;
      }
    },

    async getProfile() {
      try {
        const { data } = await api.get("/auth/profile");
        this.user = data;
      } catch (e) {
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },
  },
});
