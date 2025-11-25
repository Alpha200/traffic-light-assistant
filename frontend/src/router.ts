import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import TrafficLightsList from './views/TrafficLightsList.vue'
import AddTrafficLight from './views/AddTrafficLight.vue'
import TrafficLightDetail from './views/TrafficLightDetail.vue'
import SchedulesList from './views/SchedulesList.vue'
import ScheduleCapture from './views/ScheduleCapture.vue'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: TrafficLightsList,
    meta: { requiresAuth: true }
  },
  {
    path: '/add',
    component: AddTrafficLight,
    meta: { requiresAuth: true }
  },
  {
    path: '/traffic-light/:id',
    component: TrafficLightDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/schedules',
    component: SchedulesList,
    meta: { requiresAuth: true }
  },
  {
    path: '/schedule-capture/:id',
    component: ScheduleCapture,
    meta: { requiresAuth: true }
  },
  {
    path: '/callback',
    component: { template: '<div>Processing login...</div>' },
    meta: { requiresAuth: false }
  }
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export function setupAuthGuard(authManager: any): void {
  router.beforeEach(
    (
      to: RouteLocationNormalized,
      _from: RouteLocationNormalized,
      next: NavigationGuardNext
    ) => {
      const requiresAuth = to.meta?.requiresAuth ?? false

      if (requiresAuth && !authManager.isAuthenticated()) {
        authManager.login()
      } else {
        next()
      }
    }
  )
}

export default router
