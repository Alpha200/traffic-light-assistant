<template>
  <div class="callback-container">
    <div v-if="loading" class="loading">
      <p>Processing login...</p>
    </div>
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <router-link to="/" class="btn">Back to Home</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const state = params.get('state')
    const errorParam = params.get('error')

    if (errorParam) {
      error.value = `Authentication failed: ${errorParam}`
      loading.value = false
      return
    }

    if (!code) {
      error.value = 'No authorization code received'
      loading.value = false
      return
    }

    const storedState = sessionStorage.getItem('oidc_state')
    if (state !== storedState) {
      error.value = 'State mismatch. Possible CSRF attack.'
      loading.value = false
      return
    }

    const $authManager = (window as any).__APP__?.config.globalProperties.$authManager
    if (!$authManager) {
      error.value = 'Authentication manager not initialized'
      loading.value = false
      return
    }

    await $authManager.handleCallback(code)
    router.push('/')
  } catch (err) {
    error.value = `Error: ${err instanceof Error ? err.message : 'Unknown error'}`
    loading.value = false
  }
})
</script>

<style scoped>
.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #1a1a1a;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
}

.loading p,
.error p {
  color: #e0e0e0;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.error {
  background-color: rgba(255, 68, 68, 0.2);
  border-radius: 8px;
  border: 1px solid #ff4444;
}

.btn {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  margin-top: 1rem;
  transition: transform 0.3s;
}

.btn:hover {
  transform: translateY(-2px);
}
</style>
