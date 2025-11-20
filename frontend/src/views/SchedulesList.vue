<template>
  <div class="schedules-container">
    <div class="schedules-header">
      <router-link :to="`/traffic-light/${trafficLightId}`" class="btn-back">← Back</router-link>
      <h2>Schedules</h2>
    </div>

    <!-- Add Button -->
    <div class="add-button-section">
      <router-link :to="`/traffic-light/${trafficLightId}/schedules/capture`" class="btn btn-primary btn-large">
        + Capture Schedule
      </router-link>
    </div>

    <!-- Schedules List -->
    <section class="list-section">
      <div v-if="schedules.length === 0" class="empty-state">
        <p>No schedules captured yet. Click the button above to capture the first one!</p>
      </div>

      <div v-else class="schedules-list">
        <div v-for="schedule in schedules" :key="schedule.id" class="schedule-card">
          <div class="schedule-header">
            <button @click="deleteSchedule(schedule.id)" class="btn-delete-icon" title="Delete">🗑️</button>
          </div>

          <div class="schedule-content">
            <div class="schedule-item">
              <label>Green Start</label>
              <p class="timestamp">{{ formatDate(schedule.green_start) }}</p>
            </div>

            <div class="schedule-item">
              <label>Green End</label>
              <p class="timestamp">{{ formatDate(schedule.green_end) }}</p>
            </div>

            <div class="schedule-item highlight">
              <label>Duration</label>
              <p class="duration">{{ formatDuration(schedule.duration_ms) }}</p>
            </div>

            <div class="schedule-item">
              <label>Captured</label>
              <p class="timestamp">{{ formatDate(schedule.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'SchedulesList',
  data() {
    return {
      trafficLightId: null,
      schedules: [],
      apiUrl: '/api/traffic-lights'
    };
  },
  methods: {
    async fetchSchedules() {
      try {
        const response = await fetch(`${this.apiUrl}/${this.trafficLightId}/schedules`);
        if (!response.ok) throw new Error('Failed to fetch schedules');
        this.schedules = await response.json();
      } catch (err) {
        console.error(err);
      }
    },

    async deleteSchedule(scheduleId) {
      if (!confirm('Are you sure you want to delete this schedule?')) return;

      try {
        const response = await fetch(`${this.apiUrl.replace('/api/traffic-lights', '/api/schedules')}/${scheduleId}`, {
          method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete schedule');
        this.schedules = this.schedules.filter(s => s.id !== scheduleId);
      } catch (err) {
        console.error(err);
        alert('Error: ' + err.message);
      }
    },

    formatDate(dateString) {
      try {
        const date = new Date(dateString);
        return date.toLocaleString();
      } catch {
        return dateString;
      }
    },

    formatDuration(milliseconds) {
      const seconds = Math.floor(milliseconds / 1000);
      const ms = milliseconds % 1000;
      if (seconds > 0) {
        return `${seconds}s ${ms}ms`;
      }
      return `${ms}ms`;
    }
  },
  mounted() {
    this.trafficLightId = this.$route.params.id;
    this.fetchSchedules();
  }
};
</script>

<style scoped>
.schedules-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.schedules-header {
  display: flex;
  align-items: center;
  gap: 1rem;
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

.schedules-header h2 {
  flex: 1;
  font-size: 1.3rem;
  color: #e0e0e0;
  margin: 0;
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

.schedules-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.schedule-card {
  background: #2d2d2d;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
}

.schedule-header {
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem;
  background: #1f1f1f;
  border-bottom: 1px solid #444;
}

.btn-delete-icon {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
  padding: 0.5rem;
}

.btn-delete-icon:hover {
  opacity: 1;
}

.schedule-content {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.schedule-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.schedule-item label {
  font-weight: 600;
  color: #667eea;
  font-size: 0.85rem;
}

.schedule-item p {
  color: #e0e0e0;
  margin: 0;
  padding: 0.5rem;
  background: #3a3a3a;
  border-radius: 6px;
}

.timestamp {
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
}

.duration {
  font-weight: bold;
  font-size: 1.1rem;
  color: #667eea;
}

.schedule-item.highlight {
  grid-column: 1 / -1;
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

/* Mobile Optimization */
@media (max-width: 600px) {
  .schedules-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .schedules-header h2 {
    width: 100%;
  }

  .schedule-content {
    grid-template-columns: 1fr;
  }

  .schedule-item.highlight {
    grid-column: 1;
  }

  .btn-large {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }
}
</style>
