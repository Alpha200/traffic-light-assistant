<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- Add Button -->
        <v-card class="mb-4" elevation="2">
          <v-card-text class="text-center">
            <v-btn
              :to="'/add'"
              color="primary"
              size="large"
              prepend-icon="mdi-plus"
              block
            >
              Add Traffic Light
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Empty State -->
        <v-card v-if="trafficLights.length === 0" class="text-center pa-8">
          <v-icon icon="mdi-traffic-light-outline" size="64" color="grey"></v-icon>
          <v-card-title class="text-h6 mt-4">No traffic lights found</v-card-title>
          <v-card-text>Add one to get started!</v-card-text>
        </v-card>

        <!-- Traffic Lights List -->
        <v-row v-else>
          <v-col
            v-for="light in trafficLights"
            :key="light.id"
            cols="12"
            md="6"
            lg="4"
          >
            <v-card
              :to="`/traffic-light/${light.id}`"
              hover
              class="traffic-light-card"
            >
              <v-card-title>
                <v-icon icon="mdi-traffic-light" class="mr-2" color="primary"></v-icon>
                {{ light.location }}
              </v-card-title>

              <v-card-text>
                <div v-if="light.latitude !== null || light.longitude !== null" class="mb-2">
                  <v-chip size="small" prepend-icon="mdi-map-marker" variant="outlined">
                    {{ light.latitude }}, {{ light.longitude }}
                  </v-chip>
                </div>

                <div v-if="light.notes" class="mb-2">
                  <v-icon icon="mdi-note-text" size="small" class="mr-1"></v-icon>
                  <span class="text-caption">{{ light.notes }}</span>
                </div>

                <div class="text-caption text-grey">
                  <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
                  Updated: {{ formatDate(light.last_updated) }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, getCurrentInstance } from 'vue'
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
.traffic-light-card {
  transition: transform 0.2s;
}

.traffic-light-card:hover {
  transform: translateY(-4px);
}
</style>

