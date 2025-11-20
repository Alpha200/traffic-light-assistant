<template>
  <div class="detail-container">
    <div v-if="trafficLight" class="detail-card">
      <div class="card-header">
        <router-link to="/" class="btn-back">← Back</router-link>
        <h2>{{ trafficLight.location }}</h2>
        <button @click="deleteTrafficLight" class="btn-delete-icon" title="Delete">🗑️</button>
      </div>

      <div class="card-content">

        <div v-if="pattern && pattern.has_pattern && pattern.next_green_start" class="prediction-section">
          <h3>📍 Next Expected Green Phase</h3>
          <div class="prediction-display">
            <div :class="['countdown-box', getTrafficLightState()]">
              <div class="countdown-label">{{ getTrafficLightStateLabel() }}</div>
              <div class="countdown-time">{{ getCountdownText() }}</div>
            </div>
          </div>
        </div>

        <div v-if="pattern" class="pattern-section">
          <h3>📊 Detected Schedule</h3>
          
          <div v-if="pattern.has_pattern" class="pattern-info">
            <div class="pattern-item">
              <label>Typical Duration</label>
              <p class="value">{{ formatDuration(pattern.typical_duration_ms) }}</p>
            </div>
            
            <div class="pattern-item">
              <label>Range</label>
              <p class="value">{{ formatDuration(pattern.min_duration_ms) }} - {{ formatDuration(pattern.max_duration_ms) }}</p>
            </div>
            
            <div v-if="pattern.schedule_regularity" class="pattern-item">
              <label>Regularity</label>
              <p class="value">{{ capitalizeFirst(pattern.schedule_regularity) }}</p>
            </div>
            
            <div v-if="pattern.average_cycle_ms" class="pattern-item">
              <label>Cycle Time</label>
              <p class="value">{{ formatDuration(pattern.average_cycle_ms) }}</p>
            </div>
            
            <div class="pattern-item">
              <label>Based on</label>
              <p class="value">{{ pattern.total_captures }} capture{{ pattern.total_captures !== 1 ? 's' : '' }}</p>
            </div>
          </div>
          
          <div v-else class="empty-pattern">
            <p>No schedule detected yet. Capture green light durations to analyze patterns.</p>
          </div>
        </div>

        <div class="metadata-section">
          <h3>Metadata</h3>
          
          <div class="metadata-item">
            <label>ID</label>
            <p class="monospace">{{ trafficLight.id }}</p>
          </div>

          <div class="metadata-item">
            <label>Latitude</label>
            <p class="monospace">{{ trafficLight.latitude }}</p>
          </div>

          <div class="metadata-item">
            <label>Longitude</label>
            <p class="monospace">{{ trafficLight.longitude }}</p>
          </div>

          <div class="metadata-item">
            <label>Notes</label>
            <p>{{ trafficLight.notes || 'No notes' }}</p>
          </div>

          <div class="metadata-item">
            <label>Created At</label>
            <p class="monospace">{{ formatDate(trafficLight.created_at) }}</p>
          </div>

          <div class="metadata-item">
            <label>Last Updated</label>
            <p class="monospace">{{ formatDate(trafficLight.last_updated) }}</p>
          </div>
        </div>

        <div class="actions-section">
          <button @click="scheduleInformation" class="btn btn-primary">
            📅 Schedule Information
          </button>
        </div>
      </div>
    </div>

    <div v-else class="loading-or-error">
      <p>Loading...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrafficLightDetail',
  data() {
    return {
      trafficLight: null,
      pattern: null,
      apiUrl: '/api/traffic-lights',
      countdownTimer: null,
      currentTime: new Date()
    };
  },
  methods: {
    async fetchTrafficLight() {
      const id = this.$route.params.id;
      try {
        const response = await fetch(`${this.apiUrl}/${id}`);
        if (!response.ok) throw new Error('Failed to fetch traffic light');
        this.trafficLight = await response.json();
      } catch (err) {
        console.error(err);
        alert('Error: ' + err.message);
      }
    },

    async fetchSchedulePattern() {
      const id = this.$route.params.id;
      try {
        const response = await fetch(`${this.apiUrl}/${id}/pattern`);
        if (!response.ok) throw new Error('Failed to fetch schedule pattern');
        this.pattern = await response.json();
      } catch (err) {
        console.error(err);
      }
    },

    async deleteTrafficLight() {
      if (!confirm('Are you sure you want to delete this traffic light?')) return;

      const id = this.$route.params.id;
      try {
        const response = await fetch(`${this.apiUrl}/${id}`, {
          method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete traffic light');
        this.$router.push('/');
      } catch (err) {
        console.error(err);
        alert('Error: ' + err.message);
      }
    },

    scheduleInformation() {
      // Navigate to schedules list
      this.$router.push(`/traffic-light/${this.$route.params.id}/schedules`);
    },

    formatDate(dateString) {
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch {
        return dateString;
      }
    },

    formatDateTime(dateString) {
      try {
        const date = new Date(dateString);
        const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const dateStr = date.toLocaleDateString();
        return `${dateStr} ${time}`;
      } catch {
        return dateString;
      }
    },

    formatDuration(ms) {
      if (!ms) return '-';
      const seconds = (ms / 1000).toFixed(1);
      return `${seconds}s`;
    },

    capitalizeFirst(str) {
      return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
    },

    getTrafficLightState() {
      if (!this.pattern || !this.pattern.average_cycle_ms || !this.pattern.typical_duration_ms) {
        return 'state-unknown';
      }

      if (!this.pattern.next_green_start) {
        return 'state-unknown';
      }

      const now = this.currentTime;
      const baseStart = new Date(this.pattern.next_green_start);
      const cycleDuration = this.pattern.average_cycle_ms;
      const greenDuration = this.pattern.typical_duration_ms;

      // Calculate how many cycles have passed since the base prediction
      const timeSinceBase = now - baseStart;
      const cycleNumber = Math.floor(timeSinceBase / cycleDuration);
      
      // Current cycle's start and end
      const currentCycleStart = new Date(baseStart.getTime() + cycleNumber * cycleDuration);
      const currentCycleEnd = new Date(currentCycleStart.getTime() + greenDuration);
      
      // Check if we're in green phase
      if (now >= currentCycleStart && now < currentCycleEnd) {
        return 'state-green';
      } else {
        return 'state-red';
      }
    },

    getTrafficLightStateLabel() {
      const state = this.getTrafficLightState();
      if (state === 'state-green') {
        return '🟢 GREEN';
      } else if (state === 'state-red') {
        return '🔴 RED';
      }
      return 'WAITING';
    },

    getCountdownText() {
      if (!this.pattern || !this.pattern.average_cycle_ms || !this.pattern.typical_duration_ms) {
        return '--:--';
      }

      if (!this.pattern.next_green_start) {
        return '--:--';
      }

      const now = this.currentTime;
      const baseStart = new Date(this.pattern.next_green_start);
      const cycleDuration = this.pattern.average_cycle_ms;
      const greenDuration = this.pattern.typical_duration_ms;

      // Calculate how many cycles have passed
      const timeSinceBase = now - baseStart;
      const cycleNumber = Math.floor(timeSinceBase / cycleDuration);
      
      // Current cycle's timing
      const currentCycleStart = new Date(baseStart.getTime() + cycleNumber * cycleDuration);
      const currentCycleEnd = new Date(currentCycleStart.getTime() + greenDuration);
      const nextCycleStart = new Date(currentCycleStart.getTime() + cycleDuration);
      
      let targetTime;

      // Determine which countdown to show
      if (now >= currentCycleStart && now < currentCycleEnd) {
        // Currently in green - count down to end of green
        targetTime = currentCycleEnd;
      } else {
        // Currently in red - count down to start of next green
        targetTime = nextCycleStart;
      }

      const diff = targetTime - now;

      if (diff < 0) {
        return '00:00';
      }

      const totalSeconds = Math.floor(diff / 1000);
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;

      return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    },

    startCountdownTimer() {
      // Update countdown every 100ms for smooth animation
      this.countdownTimer = setInterval(() => {
        this.currentTime = new Date();
      }, 100);
    }
  },
  mounted() {
    this.fetchTrafficLight();
    this.fetchSchedulePattern();
    this.startCountdownTimer();
  },

  beforeUnmount() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  }
};
</script>

<style scoped>
.detail-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 0;
  min-height: 100%;
}

.detail-card {
  background: #2d2d2d;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
  width: 100%;
  max-width: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.btn-delete-icon {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
  padding: 0.5rem;
}

.btn-delete-icon:hover {
  opacity: 1;
}

.card-content {
  padding: 2rem;
}

.card-content h2 {
  font-size: 1.8rem;
  margin-bottom: 2rem;
  color: #e0e0e0;
}

.pattern-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #444;
}

.pattern-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #e0e0e0;
}

.pattern-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.pattern-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.pattern-item label {
  display: block;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.pattern-item .value {
  color: white;
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.empty-pattern {
  background: #3a3a3a;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  color: #888;
}

.prediction-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #444;
}

.prediction-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #e0e0e0;
}

.prediction-display {
  display: flex;
  justify-content: center;
}

.countdown-box {
  padding: 2rem 3rem;
  border-radius: 12px;
  text-align: center;
  min-width: 280px;
  transition: all 0.3s ease;
  border: 3px solid;
}

.countdown-box.state-green {
  background: rgba(34, 197, 94, 0.2);
  border-color: #22c55e;
}

.countdown-box.state-red {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
}

.countdown-box.state-unknown {
  background: rgba(107, 114, 128, 0.2);
  border-color: #6b7280;
}

.countdown-label {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.countdown-box.state-green .countdown-label {
  color: #22c55e;
}

.countdown-box.state-red .countdown-label {
  color: #ef4444;
}

.countdown-box.state-unknown .countdown-label {
  color: #6b7280;
}

.countdown-time {
  font-size: 3rem;
  font-weight: 700;
  font-family: 'Monaco', 'Courier New', monospace;
  letter-spacing: 2px;
}

.countdown-box.state-green .countdown-time {
  color: #22c55e;
}

.countdown-box.state-red .countdown-time {
  color: #ef4444;
}

.countdown-box.state-unknown .countdown-time {
  color: #6b7280;
}

.prediction-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.prediction-item {
  background: #2d5a2d;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #22c55e;
}

.prediction-item label {
  display: block;
  font-weight: 600;
  color: #22c55e;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.prediction-item .value {
  color: #e0e0e0;
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
}

.metadata-section {
  margin-bottom: 2rem;
}

.metadata-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #e0e0e0;
  border-bottom: 2px solid #444;
  padding-bottom: 0.5rem;
}

.metadata-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #3a3a3a;
  border-radius: 8px;
}

.metadata-item label {
  display: block;
  font-weight: 600;
  color: #667eea;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.metadata-item p {
  color: #e0e0e0;
  margin: 0;
  word-break: break-all;
}

.monospace {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

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

.loading-or-error {
  text-align: center;
  padding: 2rem;
  color: #888;
}

/* Mobile Optimization */
@media (max-width: 600px) {
  .detail-container {
    padding: 0.5rem 0;
  }

  .detail-card {
    margin: 0 0.5rem;
    border-radius: 0;
  }

  .card-content {
    padding: 1.5rem;
  }

  .card-content h2 {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .card-header {
    padding: 0.75rem;
  }

  .btn-back {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
}
</style>
