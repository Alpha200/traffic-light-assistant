import { createApp } from 'vue'
import App from './App.vue'
import router, { setupAuthGuard } from './router'
import { OIDCClient, AuthManager } from './auth'
import { ApiClient } from './api'

// Configuration from environment variables
const OIDC_PROVIDER_URL = import.meta.env.VITE_OIDC_PROVIDER_URL || 'https://sso.sendzik.eu/realms/home'
const OIDC_CLIENT_ID = import.meta.env.VITE_OIDC_CLIENT_ID || 'trafficlight'
const OIDC_REDIRECT_URI = import.meta.env.VITE_OIDC_REDIRECT_URI || `${window.location.origin}/callback`

// Initialize OIDC
const oidcClient = new OIDCClient({
  providerUrl: OIDC_PROVIDER_URL,
  clientId: OIDC_CLIENT_ID,
  redirectUri: OIDC_REDIRECT_URI
})

const authManager = new AuthManager(oidcClient)

// Initialize API client
const apiClient = new ApiClient()
apiClient.setAuthManager(authManager)

// Handle OIDC callback
const params = new URLSearchParams(window.location.search)
const code = params.get('code')
const state = params.get('state')

if (code && state) {
  const savedState = sessionStorage.getItem('oidc_state')
  if (state === savedState) {
    authManager.handleCallback(code).then(() => {
      window.location.href = '/'
    }).catch((error) => {
      console.error('Failed to process callback:', error)
      window.location.href = '/'
    })
  }
} else {
  // Normal app initialization
  const app = createApp(App)

  // Setup auth guard
  setupAuthGuard(authManager)

  // Make services available to all components
  app.config.globalProperties.$authManager = authManager
  app.config.globalProperties.$apiClient = apiClient
  app.config.globalProperties.$oidcClient = oidcClient

  app.use(router)
  app.mount('#app')
}
