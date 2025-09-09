<template>
  <div class="analysis-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客户反馈分析报告</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateRangeChange"
            />
            <el-button type="primary" @click="refreshReport">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="report-content">
        <!-- 问题类型分布图表 -->
        <div class="chart-section">
          <h3>问题类型分布</h3>
          <div id="typeDistributionChart" class="chart"></div>
        </div>
        
        <!-- 时间趋势图表 -->
        <div class="chart-section">
          <h3>反馈数量时间趋势</h3>
          <div id="timeTrendChart" class="chart"></div>
        </div>
        
        <!-- 高频问题列表 -->
        <div class="high-frequency-section">
          <h3>高频问题TOP 10</h3>
          <el-table :data="highFrequencyProblems" style="width: 100%">
            <el-table-column prop="rank" label="排名" width="80" align="center"></el-table-column>
            <el-table-column prop="summary" label="问题摘要" width="400"></el-table-column>
            <el-table-column prop="count" label="反馈次数" width="120" align="center"></el-table-column>
            <el-table-column prop="type" label="问题类型" width="150" align="center"></el-table-column>
            <el-table-column prop="severity" label="严重程度" width="120" align="center">
              <template #default="scope">
                <el-tag :type="getSeverityTagType(scope.row.severity)">{{ scope.row.severity }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 分析总结 -->
        <div class="summary-section">
          <h3>分析总结</h3>
          <el-card class="summary-card">
            <div class="summary-content" v-html="analysisSummary"></div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'

const dateRange = ref([])
const highFrequencyProblems = ref([])
const analysisSummary = ref('')
let typeDistributionChart = null
let timeTrendChart = null

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 问题类型分布图表
  const typeChartDom = document.getElementById('typeDistributionChart')
  if (typeChartDom) {
    typeDistributionChart = echarts.init(typeChartDom)
  }
  
  // 时间趋势图表
  const timeChartDom = document.getElementById('timeTrendChart')
  if (timeChartDom) {
    timeTrendChart = echarts.init(timeChartDom)
  }
  
  await loadReportData()
}

// 加载报告数据
const loadReportData = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = dateRange.value[0]
      params.endDate = dateRange.value[1]
    }
    
    const response = await axios.get('/api/analysis/report', { params })
    const data = response.data
    
    // 更新高频问题列表
    highFrequencyProblems.value = data.highFrequencyProblems || []
    
    // 更新分析总结
    analysisSummary.value = data.summary || '<p>暂无分析总结</p>'
    
    // 更新图表数据
    updateTypeDistributionChart(data.typeDistribution || {})
    updateTimeTrendChart(data.timeTrend || {})
  } catch (error) {
    console.error('加载报告数据失败:', error)
    ElMessage.error('加载报告数据失败，请重试')
  }
}

// 更新问题类型分布图表
const updateTypeDistributionChart = (data) => {
  if (!typeDistributionChart) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: data.labels || []
    },
    series: [
      {
        name: '问题类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data.values ? data.values.map((value, index) => ({
          value,
          name: data.labels[index]
        })) : []
      }
    ]
  }
  
  typeDistributionChart.setOption(option)
}

// 更新时间趋势图表
const updateTimeTrendChart = (data) => {
  if (!timeTrendChart) return
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates || []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '反馈数量',
        type: 'line',
        stack: 'Total',
        data: data.counts || [],
        areaStyle: {
          opacity: 0.3
        },
        emphasis: {
          focus: 'series'
        },
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  timeTrendChart.setOption(option)
}

// 处理日期范围变化
const handleDateRangeChange = () => {
  loadReportData()
}

// 刷新报告数据
const refreshReport = () => {
  loadReportData()
}

// 获取严重程度对应的标签类型
const getSeverityTagType = (severity) => {
  const severityMap = {
    '高': 'danger',
    '中': 'warning',
    '低': 'success'
  }
  return severityMap[severity] || 'info'
}

// 响应式调整图表大小
const handleResize = () => {
  if (typeDistributionChart) {
    typeDistributionChart.resize()
  }
  if (timeTrendChart) {
    timeTrendChart.resize()
  }
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (typeDistributionChart) {
    typeDistributionChart.dispose()
  }
  if (timeTrendChart) {
    timeTrendChart.dispose()
  }
})
</script>

<style scoped>
.analysis-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.report-content {
  padding: 20px 0;
}

.chart-section {
  margin-bottom: 40px;
}

.chart-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.chart {
  width: 100%;
  height: 400px;
}

.high-frequency-section {
  margin-bottom: 40px;
}

.high-frequency-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.summary-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.summary-card {
  background-color: #f8f9fa;
}

.summary-content {
  line-height: 1.8;
  color: #606266;
}

.summary-content p {
  margin: 10px 0;
}

.summary-content h4 {
  margin: 15px 0 10px 0;
  color: #303133;
  font-size: 14px;
}
</style>