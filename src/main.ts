import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from '@/App.vue'
import '@/styles/app.css'
import { i18n } from '@/i18n'
import { vuetify } from '@/plugins/vuetify'
import { router } from '@/router'

createApp(App).use(createPinia()).use(router).use(vuetify).use(i18n).mount('#app')
