import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import DatasheetsView from '../views/DatasheetsView.vue'
import AuthView from '../views/AuthView.vue'
import { getToken } from '../api/client'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: AuthView,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Chat',
    component: ChatView,
    meta: { requiresAuth: true },
  },
  {
    path: '/datasheets',
    name: 'Datasheets',
    component: DatasheetsView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guard de navegação para proteger rotas
router.beforeEach((to, from, next) => {
  const token = getToken()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !token) {
    // Redireciona para login se a rota requer autenticação e não tem token
    next('/auth')
  } else if (to.path === '/auth' && token) {
    // Redireciona para home se já está autenticado e tenta acessar /auth
    next('/')
  } else {
    next()
  }
})

export default router
