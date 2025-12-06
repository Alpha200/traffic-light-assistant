<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="text-h5 d-flex align-center">
            <v-icon icon="mdi-traffic-light" class="mr-2" color="primary"></v-icon>
            Add New Traffic Light
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="addTrafficLight" ref="formRef">
              <v-text-field
                v-model="newTrafficLight.location"
                label="Location"
                placeholder="e.g., Main St & 5th Ave"
                prepend-icon="mdi-map-marker"
                :rules="[rules.required]"
                required
                autofocus
                variant="outlined"
                class="mb-2"
              ></v-text-field>

              <v-row>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model.number="newTrafficLight.latitude"
                    label="Latitude"
                    type="number"
                    step="0.000001"
                    placeholder="e.g., 40.7128"
                    prepend-icon="mdi-latitude"
                    variant="outlined"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field
                    v-model.number="newTrafficLight.longitude"
                    label="Longitude"
                    type="number"
                    step="0.000001"
                    placeholder="e.g., -74.0060"
                    prepend-icon="mdi-longitude"
                    variant="outlined"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-textarea
                v-model="newTrafficLight.notes"
                label="Notes"
                prepend-icon="mdi-note-text"
                rows="3"
                variant="outlined"
                class="mb-4"
              ></v-textarea>

              <v-card-actions class="px-0">
                <v-btn
                  type="submit"
                  color="primary"
                  size="large"
                  prepend-icon="mdi-plus"
                  :loading="loading"
                  block
                >
                  Add Traffic Light
                </v-btn>
              </v-card-actions>
              <v-card-actions class="px-0">
                <v-btn
                  :to="'/'"
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-cancel"
                  block
                >
                  Cancel
                </v-btn>
              </v-card-actions>
            </v-form>
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
      Traffic light added successfully!
    </v-snackbar>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      location="top"
      :timeout="5000"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance } from 'vue'
import { useRouter } from 'vue-router'
import type { ApiClient } from '../api'

interface TrafficLightInput {
  location: string
  latitude: number | null
  longitude: number | null
  notes: string
}

const router = useRouter()
const instance = getCurrentInstance()
const apiClient = instance?.appContext.config.globalProperties.$apiClient as ApiClient

const newTrafficLight = ref<TrafficLightInput>({
  location: '',
  latitude: null,
  longitude: null,
  notes: ''
})

const loading = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const formRef = ref()

const rules = {
  required: (value: string) => !!value || 'This field is required'
}

const addTrafficLight = async () => {
  if (!newTrafficLight.value.location) {
    errorMessage.value = 'Please fill in all required fields'
    showError.value = true
    return
  }

  loading.value = true
  try {
    await apiClient.post('/api/traffic-lights', newTrafficLight.value)
    
    newTrafficLight.value = {
      location: '',
      latitude: null,
      longitude: null,
      notes: ''
    }
    
    showSuccess.value = true
    setTimeout(() => {
      router.push('/')
    }, 1000)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    errorMessage.value = message
    showError.value = true
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>
