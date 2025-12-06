<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- Header -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-btn
              :to="`/traffic-light/${trafficLightId}`"
              icon="mdi-arrow-left"
              variant="text"
              class="mr-2"
            ></v-btn>
            <v-icon icon="mdi-calendar-clock" class="mr-2" color="primary"></v-icon>
            Schedules
          </v-card-title>
        </v-card>

        <!-- Add Button -->
        <v-card class="mb-4" elevation="2">
          <v-card-text class="text-center">
            <v-btn
              :to="`/traffic-light/${trafficLightId}/schedules/capture`"
              color="primary"
              size="large"
              prepend-icon="mdi-plus"
              block
            >
              Capture Schedule
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Empty State -->
        <v-card v-if="schedules.length === 0" class="text-center pa-8">
          <v-icon icon="mdi-calendar-blank" size="64" color="grey"></v-icon>
          <v-card-title class="text-h6 mt-4">No schedules captured yet</v-card-title>
          <v-card-text>Click the button above to capture the first one!</v-card-text>
        </v-card>

        <!-- Schedules List -->
        <v-row v-else>
          <v-col
            v-for="schedule in schedules"
            :key="schedule.id"
            cols="12"
            md="6"
          >
            <v-card>
              <v-card-title class="d-flex align-center">
                <v-icon icon="mdi-traffic-light" class="mr-2" color="success"></v-icon>
                Duration: {{ formatDuration(schedule.duration_ms) }}
                <v-spacer></v-spacer>
                <v-btn
                  @click="deleteSchedule(schedule.id)"
                  icon="mdi-delete"
                  color="error"
                  variant="text"
                  size="small"
                ></v-btn>
              </v-card-title>

              <v-card-text>
                <v-list>
                  <v-list-item>
                    <v-list-item-title class="text-caption text-grey">
                      <v-icon icon="mdi-play" size="small" class="mr-1"></v-icon>
                      Green Start
                    </v-list-item-title>
                    <v-list-item-subtitle class="font-weight-mono">{{ formatDate(schedule.green_start) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title class="text-caption text-grey">
                      <v-icon icon="mdi-stop" size="small" class="mr-1"></v-icon>
                      Green End
                    </v-list-item-title>
                    <v-list-item-subtitle class="font-weight-mono">{{ formatDate(schedule.green_end) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title class="text-caption text-grey">
                      <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
                      Captured
                    </v-list-item-title>
                    <v-list-item-subtitle class="font-weight-mono">{{ formatDate(schedule.created_at) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Schedule?</v-card-title>
        <v-card-text>Are you sure you want to delete this schedule? This action cannot be undone.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showDeleteDialog = false" variant="text">Cancel</v-btn>
          <v-btn @click="confirmDelete" color="error">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, getCurrentInstance } from 'vue'
import { useRoute } from 'vue-router'
import type { ApiClient } from '../api'

interface Schedule {
  id: string
  green_start: string
  green_end: string
  duration_ms: number
  created_at: string
}

const route = useRoute()
const instance = getCurrentInstance()
const apiClient = instance?.appContext.config.globalProperties.$apiClient as ApiClient

const trafficLightId = ref<string | string[] | undefined>()
const schedules = ref<Schedule[]>([])
const showDeleteDialog = ref(false)
const scheduleToDelete = ref<string | null>(null)

const fetchSchedules = async () => {
  try {
    schedules.value = await apiClient.get<Schedule[]>(`/api/traffic-lights/${trafficLightId.value}/schedules`)
  } catch (err) {
    console.error(err)
  }
}

const deleteSchedule = (scheduleId: string) => {
  scheduleToDelete.value = scheduleId
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (!scheduleToDelete.value) return

  try {
    await apiClient.delete(`/api/schedules/${scheduleToDelete.value}`)
    schedules.value = schedules.value.filter(s => s.id !== scheduleToDelete.value)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error(err)
    alert('Error: ' + message)
  } finally {
    showDeleteDialog.value = false
    scheduleToDelete.value = null
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

const formatDuration = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000)
  const ms = milliseconds % 1000
  if (seconds > 0) {
    return `${seconds}s ${ms}ms`
  }
  return `${ms}ms`
}

onMounted(() => {
  trafficLightId.value = route.params.id
  fetchSchedules()
})
</script>

<style scoped>
.font-weight-mono {
  font-family: 'Courier New', monospace;
}
</style>
