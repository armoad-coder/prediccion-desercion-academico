import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import MainLayout from "@/layouts/MainLayout.vue";
import LoginView from "@/views/LoginView.vue";
import { useUserStore } from "@/stores/userStore";
import NotFound from "@/views/NotFound.vue";


const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    component: LoginView,
    meta: { guest: true }, // rutas a las que solo se accede sin sesión
  },
  {
    path: "/",
    component: MainLayout,
    meta: { requiresAuth: true }, // 👈 protege el layout completo
    children: [
      {
        path: "home",
        component: HomeView,
        meta: { requiresAuth: true }
      },
      {
        path: "/Dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: { requiresAuth: true }
      },
    ],
  },
  // 👇 Ruta 404
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 🔐 Middleware de protección de rutas
router.beforeEach((to) => {
  const userStore = useUserStore();

  // Si necesita login y NO hay token → redirigir
  if (to.meta.requiresAuth && !userStore.token) {
    return "/login";
  }

  // Si ya está logueado y va a /login → enviarlo al home
  if (to.meta.guest && userStore.token) {
    return "/home";
  }
});

export default router;