import { createRouter, createWebHistory } from 'vue-router'
import TrafficLightsList from './views/TrafficLightsList.vue'
import AddTrafficLight from './views/AddTrafficLight.vue'
import TrafficLightDetail from './views/TrafficLightDetail.vue'
import SchedulesList from './views/SchedulesList.vue'
import ScheduleCapture from './views/ScheduleCapture.vue'

const routes = [
  {
    path: '/',
    name: 'TrafficLightsList',
    component: TrafficLightsList
  },
  {
    path: '/add',
    name: 'AddTrafficLight',
    component: AddTrafficLight
  },
  {
    path: '/traffic-light/:id',
    name: 'TrafficLightDetail',
    component: TrafficLightDetail
  },
  {
    path: '/traffic-light/:id/schedules',
    name: 'SchedulesList',
    component: SchedulesList
  },
  {
    path: '/traffic-light/:id/schedules/capture',
    name: 'ScheduleCapture',
    component: ScheduleCapture
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
