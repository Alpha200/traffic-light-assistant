<template>
  <v-app>
    <v-app-bar color="primary" elevation="4">
      <v-app-bar-title>
        <v-icon icon="mdi-traffic-light" class="mr-2"></v-icon>
        Traffic Light Assistant
      </v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <div v-if="isAuthenticated" class="d-flex align-center">
        <v-chip v-if="user" class="mr-2" variant="text">
          <v-icon icon="mdi-account" start></v-icon>
          {{ user.name || user.preferred_username || user.sub }}
        </v-chip>
        <v-btn
          @click="logout"
          variant="outlined"
          prepend-icon="mdi-logout"
        >
          Logout
        </v-btn>
      </div>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <!-- Loading Overlay -->
    <v-overlay v-model="loading" class="align-center justify-center">
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      ></v-progress-circular>
    </v-overlay>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      location="top"
      :timeout="5000"
    >
      {{ error }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { AuthManager } from './auth'

const router = useRouter()

const loading = ref(false)
const error = ref<string | null>(null)
const showError = ref(false)
const user = ref<Record<string, any> | null>(null)

// Get injected services from global properties
const $authManager = (window as any).__APP__?.config.globalProperties.$authManager as AuthManager

const isAuthenticated = computed(() => {
  return $authManager?.isAuthenticated() ?? false
})

watch(error, (newError) => {
  if (newError) {
    showError.value = true
  }
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
</style>
