import { createApp } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'
import PrimeVue from 'primevue/config'
import router from './router'
import App from './App.vue'

// PrimeVue CSS
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

// CSS Global
import './style.css'

const app = createApp(App)

app.use(router)
app.use(VueQueryPlugin)
app.use(PrimeVue)

app.mount('#app')
