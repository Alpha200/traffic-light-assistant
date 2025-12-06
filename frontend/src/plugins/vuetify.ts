import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import { h } from 'vue'
import {
  TrafficCone,
  User,
  LogOut,
  Plus,
  MapPin,
  FileText,
  Clock,
  ArrowLeft,
  Trash2,
  MapPinCheck,
  LineChart,
  Info,
  Calendar,
  Timer,
  Play,
  Square,
  Check,
  X,
  CheckCircle2,
  CalendarClock,
  CalendarX2,
} from 'lucide-vue-next'

// Map icon names to Lucide components
const iconMap: Record<string, any> = {
  'mdi-traffic-light': TrafficCone,
  'mdi-account': User,
  'mdi-logout': LogOut,
  'mdi-plus': Plus,
  'mdi-map-marker': MapPin,
  'mdi-note-text': FileText,
  'mdi-clock-outline': Clock,
  'mdi-arrow-left': ArrowLeft,
  'mdi-delete': Trash2,
  'mdi-map-marker-check': MapPinCheck,
  'mdi-chart-line': LineChart,
  'mdi-information': Info,
  'mdi-calendar': Calendar,
  'mdi-timer': Timer,
  'mdi-play': Play,
  'mdi-stop': Square,
  'mdi-check': Check,
  'mdi-cancel': X,
  'mdi-check-circle': CheckCircle2,
  'mdi-calendar-clock': CalendarClock,
  'mdi-calendar-blank': CalendarX2,
  'mdi-latitude': MapPin,
  'mdi-longitude': MapPin,
  'mdi-traffic-light-outline': TrafficCone,
}

const customIcons = {
  component: (props: any) => {
    const IconComponent = iconMap[props.icon] || TrafficCone
    return h(IconComponent, {
      size: props.size || 24,
      class: props.class,
      style: { width: '1em', height: '1em' }
    })
  },
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'custom',
    sets: {
      custom: customIcons,
    },
  },
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        dark: true,
        colors: {
          primary: '#667eea',
          secondary: '#764ba2',
          accent: '#82B1FF',
          error: '#ff4444',
          info: '#2196F3',
          success: '#51cf66',
          warning: '#FFC107',
          background: '#1a1a1a',
          surface: '#2d2d2d',
        }
      },
      light: {
        dark: false,
        colors: {
          primary: '#667eea',
          secondary: '#764ba2',
          accent: '#82B1FF',
          error: '#ff4444',
          info: '#2196F3',
          success: '#51cf66',
          warning: '#FFC107',
        }
      }
    }
  },
  defaults: {
    VCard: {
      elevation: 4,
    },
    VBtn: {
      elevation: 2,
    },
  }
})
