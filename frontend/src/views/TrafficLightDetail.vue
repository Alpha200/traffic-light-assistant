<template>
  <div class="detail-container">
    <div v-if="trafficLight" class="detail-card">
      <div class="card-header">
        <router-link to="/" class="btn-back">← Back</router-link>
        <button @click="deleteTrafficLight" class="btn-delete-icon" title="Delete">🗑️</button>
      </div>

      <div class="card-content">
        <h2>{{ trafficLight.location }}</h2>

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
          <router-link to="/" class="btn btn-secondary">
            Back to List
          </router-link>
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
      apiUrl: '/api/traffic-lights'
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
    }
  },
  mounted() {
    this.fetchTrafficLight();
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
