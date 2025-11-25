import { createApp } from 'vue'
import App from './App.vue'
import './assets/tailwind.css'
import { createPinia } from "pinia";
import router from "./router";
import VueApexCharts from 'vue3-apexcharts';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(VueApexCharts);
app.mount("#app");
