import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import FeedbackImportView from '../views/FeedbackImportView.vue'
import AnalysisReportView from '../views/AnalysisReportView.vue'
import ProblemManagementView from '../views/ProblemManagementView.vue'

export const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/import',
    name: 'import',
    component: FeedbackImportView
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: AnalysisReportView
  },
  {
    path: '/management',
    name: 'management',
    component: ProblemManagementView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router