import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './assets/main.css'
import dayjs from 'dayjs';
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore';


import App from './App.vue'
import router from './router'
dayjs.extend(isSameOrBefore);

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
