import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import DatasheetsView from '../views/DatasheetsView.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: ChatView,
  },
  {
    path: '/datasheets',
    name: 'Datasheets',
    component: DatasheetsView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
