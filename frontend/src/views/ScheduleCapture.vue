<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-btn
              :to="`/traffic-light/${trafficLightId}/schedules`"
              icon="mdi-arrow-left"
              variant="text"
              class="mr-2"
            ></v-btn>
            <v-icon icon="mdi-timer" class="mr-2" color="primary"></v-icon>
            Capture Duration
          </v-card-title>

          <v-card-text>
            <v-alert type="info" variant="tonal" class="mb-4">
              <div class="text-body-2">
                <div><strong>Step 1:</strong> Press Start when the green light turns on</div>
                <div><strong>Step 2:</strong> Press Stop when the green light turns off</div>
              </div>
            </v-alert>

            <!-- Timer Display -->
            <v-sheet
              :color="measuring ? 'primary' : startTime ? 'success' : 'grey-darken-3'"
              class="timer-display pa-8 rounded-lg text-center mb-4"
              elevation="4"
            >
              <div v-if="!measuring && !startTime" class="text-h5 text-grey">Ready</div>
              <div v-else-if="measuring" class="timer-running">
                <div class="text-h3 font-weight-bold">{{ elapsedTime }}ms</div>
                <v-progress-linear indeterminate class="mt-4"></v-progress-linear>
              </div>
              <div v-else class="text-h4 font-weight-bold">
                <v-icon icon="mdi-check-circle" size="large" class="mr-2"></v-icon>
                {{ elapsedTime }}ms
              </div>
            </v-sheet>

            <!-- Action Buttons -->
            <v-row v-if="!measuring && !startTime" class="mb-2">
              <v-col cols="12">
                <v-btn
                  @click="startCapture"
                  color="primary"
                  size="x-large"
                  prepend-icon="mdi-play"
                  block
                >
                  Start
                </v-btn>
              </v-col>
            </v-row>

            <v-row v-else-if="measuring" class="mb-2">
              <v-col cols="12">
                <v-btn
                  @click="stopCapture"
                  color="error"
                  size="x-large"
                  prepend-icon="mdi-stop"
                  block
                >
                  Stop
                </v-btn>
              </v-col>
            </v-row>

            <v-row v-if="startTime && !measuring">
              <v-col cols="12">
                <v-btn
                  @click="submitCapture"
                  color="success"
                  size="x-large"
                  prepend-icon="mdi-check"
                  :loading="loading"
                  block
                >
                  Save Capture
                </v-btn>
              </v-col>
              <v-col cols="12">
                <v-btn
                  @click="cancelCapture"
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-cancel"
                  block
                >
                  Cancel
                </v-btn>
              </v-col>
            </v-row>

            <v-alert v-if="error" type="error" class="mt-4">
              {{ error }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="showSuccess"
      color="success"
      location="top"
      :timeout="3000"
    >
      Capture saved successfully!
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ApiClient } from '../api'

const route = useRoute()
const router = useRouter()
const instance = getCurrentInstance()
const apiClient = instance?.appContext.config.globalProperties.$apiClient as ApiClient

const trafficLightId = ref<string | string[] | undefined>()
const measuring = ref(false)
const startTime = ref<Date | null>(null)
const endTime = ref<Date | null>(null)
const elapsedTime = ref(0)
let timerInterval: number | null = null
const error = ref<string | null>(null)
const loading = ref(false)
const showSuccess = ref(false)

const startCapture = () => {
  error.value = null
  startTime.value = new Date()
  endTime.value = null
  elapsedTime.value = 0
  measuring.value = true

  timerInterval = setInterval(() => {
    if (measuring.value && startTime.value) {
      elapsedTime.value = Date.now() - startTime.value.getTime()
    }
  }, 10)
}

const stopCapture = () => {
  if (!measuring.value) return
  
  measuring.value = false
  endTime.value = new Date()
  if (startTime.value) {
    elapsedTime.value = endTime.value.getTime() - startTime.value.getTime()
  }
  
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const cancelCapture = () => {
  measuring.value = false
  startTime.value = null
  endTime.value = null
  elapsedTime.value = 0
  error.value = null
  
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const submitCapture = async () => {
  if (!startTime.value || !endTime.value) {
    error.value = 'Invalid capture data'
    return
  }

  loading.value = true
  error.value = null

  try {
    const payload = {
      traffic_light_id: trafficLightId.value,
      green_start: startTime.value.toISOString(),
      green_end: endTime.value.toISOString()
    }

    await apiClient.post(`/api/traffic-lights/${trafficLightId.value}/schedules`, payload)
    showSuccess.value = true
    setTimeout(() => {
      router.push(`/traffic-light/${trafficLightId.value}/schedules`)
    }, 1000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  trafficLightId.value = route.params.id
})

onBeforeUnmount(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})
</script>

<style scoped>
.timer-display {
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timer-running {
  width: 100%;
}
</style>
