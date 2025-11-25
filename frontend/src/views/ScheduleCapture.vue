<template>
  <div class="capture-container">
    <div class="capture-card">
      <div class="card-header">
        <router-link :to="`/traffic-light/${trafficLightId}/schedules`" class="btn-back">← Back</router-link>
        <h2>Capture Duration</h2>
      </div>

      <div class="card-content">
        <div class="instruction">
          <p>Press <strong>Start</strong> when the green light turns on</p>
          <p>Press <strong>Stop</strong> when the green light turns off</p>
        </div>

        <div class="timer-display">
          <div v-if="!measuring && !startTime" class="status-idle">
            Ready
          </div>
          <div v-else-if="measuring" class="status-running">
            {{ elapsedTime }}ms
          </div>
          <div v-else class="status-complete">
            ✓ Captured: {{ elapsedTime }}ms
          </div>
        </div>

        <div class="action-buttons">
          <button
            v-if="!measuring && !startTime"
            @click="startCapture"
            class="btn btn-primary btn-large"
          >
            ▶ Start
          </button>
          
          <button
            v-else-if="measuring"
            @click="stopCapture"
            class="btn btn-danger btn-large"
          >
            ⏹ Stop
          </button>

          <button
            v-if="startTime && !measuring"
            @click="submitCapture"
            class="btn btn-success btn-large"
          >
            ✓ Save Capture
          </button>

          <button
            v-if="startTime"
            @click="cancelCapture"
            class="btn btn-secondary"
          >
            Cancel
          </button>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="loading" class="loading">
          Saving...
        </div>
      </div>
    </div>
  </div>
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
    router.push(`/traffic-light/${trafficLightId.value}/schedules`)
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
.capture-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 0;
  min-height: 100%;
}

.capture-card {
  background: #2d2d2d;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
  width: 100%;
  max-width: 500px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #1f1f1f;
  border-bottom: 1px solid #444;
}

.btn-back {
  background: #3a3a3a;
  color: #e0e0e0;
  border: 1px solid #555;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #4a4a4a;
}

.card-header h2 {
  flex: 1;
  font-size: 1.2rem;
  color: #e0e0e0;
  margin: 0;
}

.card-content {
  padding: 2rem;
}

.instruction {
  text-align: center;
  margin-bottom: 2rem;
  color: #b0b0b0;
}

.instruction p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.timer-display {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: #3a3a3a;
  border-radius: 12px;
  border: 2px solid #444;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-idle {
  font-size: 1.5rem;
  color: #888;
  font-weight: 600;
}

.status-running {
  font-size: 2.5rem;
  color: #667eea;
  font-weight: bold;
  font-family: 'Courier New', monospace;
}

.status-complete {
  font-size: 1.8rem;
  color: #44cc44;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.btn {
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
}

.btn-large {
  font-size: 1.1rem;
  padding: 1.2rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  color: white;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(81, 207, 102, 0.4);
}

.btn-secondary {
  background: #3a3a3a;
  color: #e0e0e0;
  border: 1px solid #555;
  flex: none;
}

.btn-secondary:hover {
  background: #4a4a4a;
}

.error-message {
  background: #ff4444;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 1rem;
}

.loading {
  text-align: center;
  color: #667eea;
  font-weight: 600;
  margin-top: 1rem;
}

/* Mobile Optimization */
@media (max-width: 600px) {
  .capture-container {
    padding: 0.5rem 0;
  }

  .capture-card {
    margin: 0 0.5rem;
    border-radius: 0;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-header h2 {
    width: 100%;
  }

  .card-content {
    padding: 1.5rem;
  }

  .timer-display {
    min-height: 80px;
    padding: 1.5rem;
  }

  .status-running {
    font-size: 2rem;
  }
}
</style>
