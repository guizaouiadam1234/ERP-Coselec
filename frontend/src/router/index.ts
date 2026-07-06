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
  
{
    path: "/employees",
    component: EmployeesView,
  },
  {
    path: "/stock/movement",
    component: () => import("../views/Stock/StockMovementView.vue")
  }

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


router.beforeEach((to, from, next) => {
  const token =
    localStorage.getItem("access_token") ||
    sessionStorage.getItem("access_token");

  if (to.path === "/home" && !token) {
    next("/login");
  }
  else if (to.path === "/login" && token) {
    next("/home");
  } else {
    next();
  }
});


export default router;