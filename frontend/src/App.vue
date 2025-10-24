<template>
  <div id="app">
    <nav v-if="isAuthenticated" class="navbar">
      <div class="container">
        <div class="nav-brand">
          <i class="pi pi-database"></i>
          <span>Interview AI</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link">
            <i class="pi pi-comments"></i>
            Chat
          </router-link>
          <router-link to="/datasheets" class="nav-link">
            <i class="pi pi-table"></i>
            Datasheets
          </router-link>
          <button @click="handleLogout" class="nav-link logout-button">
            <i class="pi pi-sign-out"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>
    
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getToken, logout } from './api/client'

const route = useRoute()

const isAuthenticated = computed(() => {
  return route.path !== '/auth' && getToken() !== null
})

const handleLogout = () => {
  if (confirm('Tem certeza que deseja sair?')) {
    logout()
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-brand i {
  font-size: 2rem;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.3);
}

.logout-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: inherit;
  font-family: inherit;
}

.logout-button:hover {
  background: rgba(255, 0, 0, 0.3);
}

main {
  min-height: calc(100vh - 80px);
}
</style>
