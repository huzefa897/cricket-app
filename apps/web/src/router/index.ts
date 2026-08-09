import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/setup', name: 'setup', component: () => import('../views/Setup.vue') },
  {
    path: '/match/:id/score',
    name: 'score',
    component: () => import('../views/ScorerDashboard.vue'),
    props: true,
  },
  {
    path: '/match/:id/live',
    name: 'live',
    component: () => import('../views/ViewerLive.vue'),
    props: true,
  },
  { path: '/history', name: 'history', component: () => import('../views/History.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
