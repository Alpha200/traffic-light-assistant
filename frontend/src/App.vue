<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-content">
        <h1>🚦 Traffic Light Assistant</h1>
        <div class="header-user">
          <span v-if="user" class="user-info">{{ user.name || user.preferred_username || user.sub }}</span>
          <button v-if="isAuthenticated" @click="logout" class="btn-logout">Logout</button>
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <!-- Loading/Error Messages -->
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="error = null" class="btn-close">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { AuthManager } from './auth'

const router = useRouter()

const loading = ref(false)
const error = ref<string | null>(null)
const user = ref<Record<string, any> | null>(null)

// Get injected services from global properties
const $authManager = (window as any).__APP__?.config.globalProperties.$authManager as AuthManager

const isAuthenticated = computed(() => {
  return $authManager?.isAuthenticated() ?? false
})

onMounted(() => {
  if ($authManager) {
    user.value = $authManager.getUser()
  }
})

const logout = () => {
  if ($authManager) {
    $authManager.logout()
  }
  router.push('/callback')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #1a1a1a;
  color: #e0e0e0;
}

html, body, #app {
  height: 100%;
  width: 100%;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #1a1a1a;
  color: #e0e0e0;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  font-size: 1.8rem;
  margin: 0;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  font-size: 0.95rem;
  opacity: 0.9;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.3);
}

.app-main {
  flex: 1;
  padding: 1rem;
  max-width: 100%;
  overflow-y: auto;
}

/* Loading and Error */
.loading {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  z-index: 1000;
}

.error-message {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  background: #ff4444;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 1001;
  max-width: 90%;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: inherit;
}

/* Mobile Optimization */
@media (max-width: 600px) {
  .app-header {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .app-header h1 {
    font-size: 1.5rem;
  }

  .header-user {
    width: 100%;
    justify-content: space-between;
  }

  .app-main {
    padding: 0.75rem;
  }

  .error-message {
    bottom: auto;
    top: 1rem;
    right: 0.5rem;
    left: 0.5rem;
    max-width: none;
  }
}
</style>

