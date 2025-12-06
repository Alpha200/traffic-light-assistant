<template>
  <v-container>
    <v-row v-if="trafficLight">
      <v-col cols="12">
        <!-- Header Card -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-btn
              :to="'/'"
              icon="mdi-arrow-left"
              variant="text"
              class="mr-2"
            ></v-btn>
            <v-icon icon="mdi-traffic-light" class="mr-2" color="primary"></v-icon>
            {{ trafficLight.location }}
            <v-spacer></v-spacer>
            <v-btn
              @click="deleteTrafficLight"
              icon="mdi-delete"
              color="error"
              variant="text"
            ></v-btn>
          </v-card-title>
        </v-card>

        <!-- Prediction Section -->
        <v-card v-if="pattern && pattern.has_pattern && pattern.next_green_start" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-map-marker-check" class="mr-2"></v-icon>
            Next Expected Green Phase
          </v-card-title>
          <v-card-text class="text-center">
            <v-sheet
              :color="getTrafficLightState() === 'state-green' ? 'success' : getTrafficLightState() === 'state-red' ? 'error' : 'grey'"
              class="countdown-box pa-6 rounded-lg"
              elevation="4"
            >
              <div class="text-h6 mb-2">{{ getTrafficLightStateLabel() }}</div>
              <div class="text-h2 font-weight-bold countdown-time">{{ getCountdownText() }}</div>
            </v-sheet>
          </v-card-text>
        </v-card>

        <!-- Pattern Section -->
        <v-card v-if="pattern" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-chart-line" class="mr-2"></v-icon>
            Detected Schedule
          </v-card-title>
          <v-card-text>
            <v-row v-if="pattern.has_pattern">
              <v-col cols="6" md="4">
                <v-sheet color="primary" class="pa-4 rounded text-center">
                  <div class="text-caption">Typical Duration</div>
                  <div class="text-h6 font-weight-bold">{{ formatDuration(pattern.typical_duration_ms) }}</div>
                </v-sheet>
              </v-col>
              <v-col cols="6" md="4">
                <v-sheet color="primary" class="pa-4 rounded text-center">
                  <div class="text-caption">Range</div>
                  <div class="text-h6 font-weight-bold">{{ formatDuration(pattern.min_duration_ms) }} - {{ formatDuration(pattern.max_duration_ms) }}</div>
                </v-sheet>
              </v-col>
              <v-col v-if="pattern.schedule_regularity" cols="6" md="4">
                <v-sheet color="primary" class="pa-4 rounded text-center">
                  <div class="text-caption">Regularity</div>
                  <div class="text-h6 font-weight-bold">{{ capitalizeFirst(pattern.schedule_regularity) }}</div>
                </v-sheet>
              </v-col>
              <v-col v-if="pattern.average_cycle_ms" cols="6" md="4">
                <v-sheet color="primary" class="pa-4 rounded text-center">
                  <div class="text-caption">Cycle Time</div>
                  <div class="text-h6 font-weight-bold">{{ formatDuration(pattern.average_cycle_ms) }}</div>
                </v-sheet>
              </v-col>
              <v-col cols="6" md="4">
                <v-sheet color="primary" class="pa-4 rounded text-center">
                  <div class="text-caption">Based on</div>
                  <div class="text-h6 font-weight-bold">{{ pattern.total_captures }} capture{{ pattern.total_captures !== 1 ? 's' : '' }}</div>
                </v-sheet>
              </v-col>
            </v-row>
            <v-alert v-else type="info" variant="tonal">
              No schedule detected yet. Capture green light durations to analyze patterns.
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- Timeline Section -->
        <v-card v-if="timeline && timeline.has_pattern" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-clock-outline" class="mr-2"></v-icon>
            Predicted Pattern Timeline
          </v-card-title>
          <v-card-text>
            <div v-if="timeline.validation" class="text-center text-caption mb-4">
              Pattern confidence: {{ (timeline.validation.match_rate * 100).toFixed(0) }}%
              ({{ timeline.validation.matches }}/{{ timeline.validation.total }} measurements match)
            </div>
            <v-sheet color="surface-variant" class="pa-4 rounded">
              <div class="timeline-hours">
                <div v-for="hour in 24" :key="hour" class="hour-marker text-caption">
                  {{ String(hour - 1).padStart(2, '0') }}:00
                </div>
              </div>
              <div class="timeline-bar">
                <div 
                  v-for="(entry, index) in timeline.entries" 
                  :key="index"
                  :class="['timeline-entry', `state-${entry.state}`]"
                  :style="getTimelineEntryStyle(entry)"
                  :title="`${entry.state.toUpperCase()}: ${formatTimelineTime(entry.start_time)} - ${formatTimelineTime(entry.end_time)}`"
                >
                </div>
                <div class="timeline-current-time" :style="getCurrentTimePosition()"></div>
              </div>
            </v-sheet>
          </v-card-text>
        </v-card>

        <!-- Metadata Section -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-information" class="mr-2"></v-icon>
            Metadata
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">ID</v-list-item-title>
                <v-list-item-subtitle class="font-weight-mono">{{ trafficLight.id }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Latitude</v-list-item-title>
                <v-list-item-subtitle class="font-weight-mono">{{ trafficLight.latitude }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Longitude</v-list-item-title>
                <v-list-item-subtitle class="font-weight-mono">{{ trafficLight.longitude }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Notes</v-list-item-title>
                <v-list-item-subtitle>{{ trafficLight.notes || 'No notes' }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Created At</v-list-item-title>
                <v-list-item-subtitle class="font-weight-mono">{{ formatDate(trafficLight.created_at) }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-grey">Last Updated</v-list-item-title>
                <v-list-item-subtitle class="font-weight-mono">{{ formatDate(trafficLight.last_updated) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Actions -->
        <v-btn
          @click="scheduleInformation"
          color="primary"
          size="large"
          prepend-icon="mdi-calendar"
          block
        >
          Schedule Information
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-else>
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <div class="text-h6 mt-4">Loading...</div>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Traffic Light?</v-card-title>
        <v-card-text>Are you sure you want to delete this traffic light? This action cannot be undone.</v-card-text>
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
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ApiClient } from '../api'

interface TrafficLight {
  id: string
  location: string
  latitude: number | null
  longitude: number | null
  notes: string
  created_at: string
  last_updated: string
}

interface SchedulePattern {
  has_pattern: boolean
  typical_duration_ms: number
  min_duration_ms: number
  max_duration_ms: number
  average_cycle_ms: number
  total_captures: number
  schedule_regularity: string
  next_green_start: string
}

interface TimelineEntry {
  start_time: string
  end_time: string
  state: 'green' | 'red'
}

interface DailyTimeline {
  date: string
  has_pattern: boolean
  entries: TimelineEntry[]
  validation?: {
    is_valid: boolean
    matches: number
    total: number
    match_rate: number
  }
}

const route = useRoute()
const router = useRouter()
const instance = getCurrentInstance()
const apiClient = instance?.appContext.config.globalProperties.$apiClient as ApiClient

const trafficLight = ref<TrafficLight | null>(null)
const pattern = ref<SchedulePattern | null>(null)
const timeline = ref<DailyTimeline | null>(null)
const showDeleteDialog = ref(false)
let countdownTimer: number | null = null
const currentTime = ref(new Date())

const fetchTrafficLight = async () => {
  const id = route.params.id
  try {
    trafficLight.value = await apiClient.get<TrafficLight>(`/api/traffic-lights/${id}`)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error(err)
    alert('Error: ' + message)
  }
}

const fetchSchedulePattern = async () => {
  const id = route.params.id
  try {
    pattern.value = await apiClient.get<SchedulePattern>(`/api/traffic-lights/${id}/pattern`)
  } catch (err) {
    console.error(err)
  }
}

const fetchTimeline = async () => {
  const id = route.params.id
  try {
    timeline.value = await apiClient.get<DailyTimeline>(`/api/traffic-lights/${id}/pattern/timeline`)
  } catch (err) {
    console.error(err)
  }
}

const deleteTrafficLight = () => {
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  const id = route.params.id
  try {
    await apiClient.delete(`/api/traffic-lights/${id}`)
    router.push('/')
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error(err)
    alert('Error: ' + message)
  } finally {
    showDeleteDialog.value = false
  }
}

const scheduleInformation = () => {
  router.push(`/traffic-light/${route.params.id}/schedules`)
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

const formatDateTime = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    const dateStr = date.toLocaleDateString()
    return `${dateStr} ${time}`
  } catch {
    return dateString
  }
}

const formatDuration = (ms: number): string => {
  if (!ms) return '-'
  const seconds = (ms / 1000).toFixed(1)
  return `${seconds}s`
}

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ')
}

const getTrafficLightState = (): string => {
  if (!pattern.value || !pattern.value.average_cycle_ms || !pattern.value.typical_duration_ms) {
    return 'state-unknown'
  }

  if (!pattern.value.next_green_start) {
    return 'state-unknown'
  }

  const now = currentTime.value
  const baseStart = new Date(pattern.value.next_green_start)
  const cycleDuration = pattern.value.average_cycle_ms
  const greenDuration = pattern.value.typical_duration_ms

  const timeSinceBase = now.getTime() - baseStart.getTime()
  const cycleNumber = Math.floor(timeSinceBase / cycleDuration)
  
  const currentCycleStart = new Date(baseStart.getTime() + cycleNumber * cycleDuration)
  const currentCycleEnd = new Date(currentCycleStart.getTime() + greenDuration)
  
  if (now >= currentCycleStart && now < currentCycleEnd) {
    return 'state-green'
  } else {
    return 'state-red'
  }
}

const getTrafficLightStateLabel = (): string => {
  const state = getTrafficLightState()
  if (state === 'state-green') {
    return '🟢 GREEN'
  } else if (state === 'state-red') {
    return '🔴 RED'
  }
  return 'WAITING'
}

const getCountdownText = (): string => {
  if (!pattern.value || !pattern.value.average_cycle_ms || !pattern.value.typical_duration_ms) {
    return '--:--'
  }

  if (!pattern.value.next_green_start) {
    return '--:--'
  }

  const now = currentTime.value
  const baseStart = new Date(pattern.value.next_green_start)
  const cycleDuration = pattern.value.average_cycle_ms
  const greenDuration = pattern.value.typical_duration_ms

  const timeSinceBase = now.getTime() - baseStart.getTime()
  const cycleNumber = Math.floor(timeSinceBase / cycleDuration)
  
  const currentCycleStart = new Date(baseStart.getTime() + cycleNumber * cycleDuration)
  const currentCycleEnd = new Date(currentCycleStart.getTime() + greenDuration)
  const nextCycleStart = new Date(currentCycleStart.getTime() + cycleDuration)
  
  let targetTime: Date

  if (now >= currentCycleStart && now < currentCycleEnd) {
    targetTime = currentCycleEnd
  } else {
    targetTime = nextCycleStart
  }

  const diff = targetTime.getTime() - now.getTime()

  if (diff < 0) {
    return '00:00'
  }

  const totalSeconds = Math.floor(diff / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60

  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

const startCountdownTimer = () => {
  countdownTimer = setInterval(() => {
    currentTime.value = new Date()
  }, 100)
}

const getTimelineEntryStyle = (entry: TimelineEntry) => {
  const startTime = new Date(entry.start_time)
  const endTime = new Date(entry.end_time)
  
  // Calculate position as percentage of the day
  const startMs = startTime.getHours() * 3600000 + startTime.getMinutes() * 60000 + startTime.getSeconds() * 1000
  const endMs = endTime.getHours() * 3600000 + endTime.getMinutes() * 60000 + endTime.getSeconds() * 1000
  
  const dayMs = 24 * 3600000
  const leftPercent = (startMs / dayMs) * 100
  const widthPercent = ((endMs - startMs) / dayMs) * 100
  
  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`
  }
}

const getCurrentTimePosition = () => {
  const now = currentTime.value
  const ms = now.getHours() * 3600000 + now.getMinutes() * 60000 + now.getSeconds() * 1000
  const dayMs = 24 * 3600000
  const percent = (ms / dayMs) * 100
  
  return {
    left: `${percent}%`
  }
}

const formatTimelineTime = (isoString: string): string => {
  try {
    const date = new Date(isoString)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return isoString
  }
}

onMounted(() => {
  fetchTrafficLight()
  fetchSchedulePattern()
  fetchTimeline()
  startCountdownTimer()
})

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.countdown-box {
  border: 3px solid currentColor;
}

.countdown-time {
  font-family: 'Monaco', 'Courier New', monospace;
  letter-spacing: 2px;
}

.timeline-hours {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.hour-marker {
  flex: 1;
  text-align: center;
  min-width: 40px;
}

.timeline-bar {
  position: relative;
  height: 40px;
  background: linear-gradient(to right, 
    rgba(239, 68, 68, 0.3) 0%, 
    rgba(239, 68, 68, 0.3) 100%);
  border-radius: 6px;
  overflow: visible;
}

.timeline-entry {
  position: absolute;
  top: 0;
  height: 100%;
  transition: all 0.3s;
  border-radius: 4px;
  cursor: pointer;
}

.timeline-entry.state-green {
  background: rgba(34, 197, 94, 0.8);
  border: 1px solid #22c55e;
}

.timeline-entry.state-red {
  background: rgba(239, 68, 68, 0.4);
  border: 1px solid rgba(239, 68, 68, 0.6);
}

.timeline-entry:hover {
  transform: scaleY(1.1);
  z-index: 10;
}

.timeline-current-time {
  position: absolute;
  top: -5px;
  bottom: -5px;
  width: 2px;
  background: #fbbf24;
  box-shadow: 0 0 10px rgba(251, 191, 36, 0.8);
  z-index: 20;
  pointer-events: none;
}

.timeline-current-time::before {
  content: '';
  position: absolute;
  top: -5px;
  left: -4px;
  width: 10px;
  height: 10px;
  background: #fbbf24;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(251, 191, 36, 0.8);
}

.font-weight-mono {
  font-family: 'Courier New', monospace;
}
</style>
