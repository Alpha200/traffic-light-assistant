<template>
  <div class="add-container">
    <div class="add-form-card">
      <h2>Add New Traffic Light</h2>

      <form @submit.prevent="addTrafficLight" class="add-form">
        <div class="form-group">
          <label for="location">Location *</label>
          <input
            id="location"
            v-model="newTrafficLight.location"
            type="text"
            placeholder="e.g., Main St & 5th Ave"
            required
            autofocus
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="latitude">Latitude</label>
            <input
              id="latitude"
              v-model.number="newTrafficLight.latitude"
              type="number"
              step="0.000001"
              placeholder="e.g., 40.7128"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="longitude">Longitude</label>
            <input
              id="longitude"
              v-model.number="newTrafficLight.longitude"
              type="number"
              step="0.000001"
              placeholder="e.g., -74.0060"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="notes">Notes</label>
          <textarea
            id="notes"
            v-model="newTrafficLight.notes"
            placeholder="Add any additional notes..."
            rows="3"
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            Add Traffic Light
          </button>
          <router-link to="/" class="btn btn-secondary">
            Cancel
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddTrafficLight',
  data() {
    return {
      newTrafficLight: {
        location: '',
        latitude: null,
        longitude: null,
        notes: ''
      },
      apiUrl: '/api/traffic-lights'
    };
  },
  methods: {
    async addTrafficLight() {
      if (!this.newTrafficLight.location) {
        alert('Please fill in all required fields');
        return;
      }

      try {
        const response = await fetch(this.apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newTrafficLight)
        });

        if (!response.ok) throw new Error('Failed to add traffic light');
        
        // Reset form and navigate back
        this.newTrafficLight = {
          location: '',
          latitude: null,
          longitude: null,
          notes: ''
        };
        
        this.$router.push('/');
      } catch (err) {
        alert('Error: ' + err.message);
        console.error(err);
      }
    }
  }
};
</script>

<style scoped>
.add-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 0;
  min-height: 100%;
}

.add-form-card {
  background: #2d2d2d;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid #444;
  width: 100%;
  max-width: 500px;
}

.add-form-card h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #e0e0e0;
  text-align: center;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-weight: 600;
  color: #e0e0e0;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 2px solid #444;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s;
  background-color: #3a3a3a;
  color: #e0e0e0;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
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
  flex: 1;
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
  .add-container {
    padding: 0.5rem 0;
  }

  .add-form-card {
    padding: 1.5rem;
    margin: 0 0.5rem;
  }

  .add-form-card h2 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
