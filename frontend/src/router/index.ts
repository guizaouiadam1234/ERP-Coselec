import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/LoginView.vue";
import HomeView from "../views/HomeView.vue";
import EmployeesView from "../views/EmployeesView.vue";
const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    component: LoginView,
  },
  {
    path: "/home",
    component: HomeView,
  },
  //rh
{
    path: "/employees",
    component: EmployeesView,
  },
  {
    path: "/departments",
    component: () => import("../views/employees/DepartmentView.vue")
  },
  // stock
  {
    path: "/stock/movement",
    component: () => import("../views/Stock/StockMovementView.vue")
  },
  {
    path: "/stock",
    component: () => import("../views/Stock/StockOverviewView.vue")
  },
  {
    path: "/stock/canvas",
    component: () => import("../views/Stock/StockCanvasView.vue")
  },
  // tickets
  {
    path: "/tickets",
    name: "tickets",
    component: () => import("../views/TicketsView.vue")
  },
  {
    path: "/requests",
    name: "requests",
    component: () => import("../views/RequestsView.vue")
  }
  ,
  {
    path: "/requests/:section(hr|it|facilities)",
    name: "request-form",
    component: () => import("../views/RequestFormView.vue"),
    props: true
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

function isTokenExpired(token: string): boolean {
  try {
    const payloadBase64 = token.split(".")[1];
    if (!payloadBase64) {
      return true;
    }

    const payloadJson = atob(payloadBase64.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(payloadJson) as { exp?: number };

    if (!payload.exp) {
      return false;
    }

    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now;
  } catch {
    return true;
  }
}


router.beforeEach((to, from, next) => {
  const rawToken =
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token");

  const token = rawToken && !isTokenExpired(rawToken) ? rawToken : null;

  if (rawToken && !token) {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");
  }

  const isPublicRoute = to.path === "/login";

  if (!isPublicRoute && !token) {
    next("/login");
  }
  else if (to.path === "/login" && token) {
    next("/home");
  } else {
    next();
  }
});


export default router;