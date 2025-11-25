<template>
  <div class="list-container">
    <!-- Add Button -->
    <div class="add-button-section">
      <router-link to="/add" class="btn btn-primary btn-large">
        + Add Traffic Light
      </router-link>
    </div>

    <!-- Traffic Lights List -->
    <section class="list-section">
      <div v-if="filteredTrafficLights.length === 0" class="empty-state">
        <p>No traffic lights found. Add one to get started!</p>
      </div>

      <div v-else class="traffic-lights-list">
        <router-link
          v-for="light in trafficLights"
          :key="light.id"
          :to="`/traffic-light/${light.id}`"
          class="traffic-light-card"
        >
          <div class="card-content">
            <h3>{{ light.location }}</h3>

            <div class="card-details">
              <p v-if="light.latitude !== null || light.longitude !== null" class="location-coords">
                📍 {{ light.latitude }}, {{ light.longitude }}
              </p>
              <p v-if="light.notes" class="notes">
                📝 {{ light.notes }}
              </p>
              <p class="timestamp">
                Last updated: {{ formatDate(light.last_updated) }}
              </p>
            </div>
          </div>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import type { ApiClient } from '../api'

interface TrafficLight {
  id: string
  location: string
  latitude: number | null
  longitude: number | null
  notes: string
  last_updated: string
}

const instance = getCurrentInstance()
const apiClient = instance?.appContext.config.globalProperties.$apiClient as ApiClient

const trafficLights = ref<TrafficLight[]>([])

const filteredTrafficLights = computed(() => trafficLights.value)

const fetchTrafficLights = async () => {
  try {
    trafficLights.value = await apiClient.get<TrafficLight[]>('/api/traffic-lights')
  } catch (err) {
    console.error(err)
  }
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(() => {
  fetchTrafficLights()
})
</script>

<style scoped>
.list-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Add Button Section */
.add-button-section {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  width: 100%;
  max-width: 300px;
}

/* List Section */
.list-section {
  margin-bottom: 2rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #888;
}

.traffic-lights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.traffic-light-card {
  background: #2d2d2d;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
  border: 1px solid #444;
  text-decoration: none;
  color: inherit;
  display: block;
  cursor: pointer;
}

.traffic-light-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #1f1f1f;
  border-bottom: 1px solid #444;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.card-content {
  padding: 1rem;
}

.card-content h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #e0e0e0;
}

.card-details {
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #b0b0b0;
}

.card-details p {
  margin-bottom: 0.5rem;
}

.location-coords {
  font-family: monospace;
}

.notes {
  font-style: italic;
}

.timestamp {
  font-size: 0.8rem;
  color: #666;
}

.card-edit {
  padding: 1rem;
  background: #1f1f1f;
  border-top: 1px solid #444;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-actions .btn {
  flex: 1;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #3a3a3a;
  color: #e0e0e0;
  border: 1px solid #555;
}

.btn-secondary:hover {
  background: #4a4a4a;
}

/* Mobile Optimization */
@media (max-width: 600px) {
  .add-button-section {
    padding: 0.5rem 0;
  }

  .btn-large {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }

  .filter-buttons {
    gap: 0.5rem;
  }

  .filter-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .card-header {
    padding: 0.75rem;
  }

  .card-content {
    padding: 0.75rem;
  }
}
</style>
