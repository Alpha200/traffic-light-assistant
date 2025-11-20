<template>
  <div class="app-container">
    <header class="app-header">
      <h1>🚦 Traffic Light Assistant</h1>
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

<script>
export default {
  name: 'App',
  data() {
    return {
      loading: false,
      error: null
    };
  }
};
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
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.app-header h1 {
  font-size: 1.8rem;
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

  .app-header h1 {
    font-size: 1.5rem;
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

