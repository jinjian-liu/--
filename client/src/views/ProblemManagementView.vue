<template>
  <div class="management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>问题管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索问题关键词"
              prefix-icon="Search"
              style="width: 300px;"
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-select v-model="filterType" placeholder="问题类型" style="width: 150px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="技术问题" value="technical"></el-option>
          <el-option label="服务态度" value="service"></el-option>
          <el-option label="价格异议" value="price"></el-option>
          <el-option label="功能建议" value="feature"></el-option>
          <el-option label="其他" value="other"></el-option>
        </el-select>
        
        <el-select v-model="filterSeverity" placeholder="严重程度" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="高" value="high"></el-option>
          <el-option label="中" value="medium"></el-option>
          <el-option label="低" value="low"></el-option>
        </el-select>
        
        <el-select v-model="filterStatus" placeholder="处理状态" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="待处理" value="pending"></el-option>
          <el-option label="处理中" value="processing"></el-option>
          <el-option label="已解决" value="resolved"></el-option>
          <el-option label="已关闭" value="closed"></el-option>
        </el-select>
        
        <el-button type="default" @click="resetFilters" style="margin-left: auto;">
          重置筛选
        </el-button>
      </div>
      
      <!-- 问题列表 -->
      <div class="problems-table">
        <el-table 
          :data="problemsData" 
          style="width: 100%"
          v-loading="loading"
          element-loading-text="加载中..."
        >
          <el-table-column prop="id" label="问题ID" width="100" align="center"></el-table-column>
          <el-table-column prop="summary" label="问题摘要" min-width="300">
            <template #default="scope">
              <div class="problem-summary" @click="showProblemDetail(scope.row)">
                {{ scope.row.summary }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="问题类型" width="120" align="center"></el-table-column>
          <el-table-column prop="severity" label="严重程度" width="100" align="center">
            <template #default="scope">
              <el-tag :type="getSeverityTagType(scope.row.severity)">{{ scope.row.severity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="feedbackCount" label="反馈次数" width="100" align="center"></el-table-column>
          <el-table-column prop="status" label="处理状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" width="160" align="center"></el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="showProblemDetail(scope.row)">
                详情
              </el-button>
              <el-button size="small" type="success" @click="markAsResolved(scope.row.id)" v-if="scope.row.status !== 'resolved'">
                解决
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalProblems"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 问题详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="问题详情" width="80%" max-height="80vh">
      <div class="problem-detail" v-if="currentProblem">
        <div class="detail-header">
          <h3>{{ currentProblem.summary }}</h3>
          <div class="detail-meta">
            <span>ID: {{ currentProblem.id }}</span>
            <span>创建时间: {{ currentProblem.createTime }}</span>
            <span>更新时间: {{ currentProblem.updateTime }}</span>
          </div>
        </div>
        
        <div class="detail-info">
          <div class="info-item">
            <label>问题类型:</label>
            <span>{{ currentProblem.type }}</span>
          </div>
          <div class="info-item">
            <label>严重程度:</label>
            <el-tag :type="getSeverityTagType(currentProblem.severity)">{{ currentProblem.severity }}</el-tag>
          </div>
          <div class="info-item">
            <label>反馈次数:</label>
            <span>{{ currentProblem.feedbackCount }} 次</span>
          </div>
          <div class="info-item">
            <label>处理状态:</label>
            <el-tag :type="getStatusTagType(currentProblem.status)">{{ getStatusText(currentProblem.status) }}</el-tag>
          </div>
        </div>
        
        <div class="detail-content">
          <h4>问题描述:</h4>
          <p>{{ currentProblem.description }}</p>
          
          <h4>实体识别:</h4>
          <div class="entities" v-if="currentProblem.entities && currentProblem.entities.length > 0">
            <span v-for="entity in currentProblem.entities" :key="entity.id" class="entity-tag">
              {{ entity.name }} ({{ entity.type }})
            </span>
          </div>
          <p v-else>暂无实体识别结果</p>
          
          <h4>相关反馈示例:</h4>
          <div class="feedback-examples" v-if="currentProblem.feedbackExamples && currentProblem.feedbackExamples.length > 0">
            <el-collapse>
              <el-collapse-item 
                v-for="(example, index) in currentProblem.feedbackExamples" 
                :key="index" 
                :title="`示例 ${index + 1}`"
              >
                <p>{{ example }}</p>
              </el-collapse-item>
            </el-collapse>
          </div>
          <p v-else>暂无反馈示例</p>
        </div>
        
        <div class="detail-actions">
          <el-select v-model="newStatus" placeholder="更新状态" style="width: 200px; margin-right: 10px;">
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="处理中" value="processing"></el-option>
            <el-option label="已解决" value="resolved"></el-option>
            <el-option label="已关闭" value="closed"></el-option>
          </el-select>
          <el-button type="primary" @click="updateProblemStatus">
            更新状态
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

const searchKeyword = ref('')
const filterType = ref('')
const filterSeverity = ref('')
const filterStatus = ref('')
const loading = ref(false)
const problemsData = ref([])
const totalProblems = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const detailDialogVisible = ref(false)
const currentProblem = ref(null)
const newStatus = ref('')

// 加载问题列表数据
const loadProblemsData = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchKeyword.value,
      type: filterType.value,
      severity: filterSeverity.value,
      status: filterStatus.value,
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    const response = await axios.get('/api/problems/list', { params })
    problemsData.value = response.data.items || []
    totalProblems.value = response.data.total || 0
  } catch (error) {
    console.error('加载问题列表失败:', error)
    ElMessage.error('加载问题列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 搜索问题
const handleSearch = () => {
  currentPage.value = 1
  loadProblemsData()
}

// 重置筛选条件
const resetFilters = () => {
  searchKeyword.value = ''
  filterType.value = ''
  filterSeverity.value = ''
  filterStatus.value = ''
  currentPage.value = 1
  loadProblemsData()
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadProblemsData()
}

// 当前页码变化
const handleCurrentChange = (current) => {
  currentPage.value = current
  loadProblemsData()
}

// 显示问题详情
const showProblemDetail = async (problem) => {
  try {
    const response = await axios.get(`/api/problems/${problem.id}`)
    currentProblem.value = response.data
    newStatus.value = currentProblem.value.status
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取问题详情失败:', error)
    ElMessage.error('获取问题详情失败，请重试')
  }
}

// 标记问题为已解决
const markAsResolved = async (problemId) => {
  try {
    await axios.post(`/api/problems/${problemId}/resolve`)
    ElMessage.success('问题已标记为已解决')
    loadProblemsData()
  } catch (error) {
    console.error('更新问题状态失败:', error)
    ElMessage.error('更新问题状态失败，请重试')
  }
}

// 更新问题状态
const updateProblemStatus = async () => {
  if (!currentProblem.value || !newStatus.value) return
  
  try {
    await axios.post(`/api/problems/${currentProblem.value.id}/update-status`, {
      status: newStatus.value
    })
    ElMessage.success('问题状态已更新')
    currentProblem.value.status = newStatus.value
    loadProblemsData()
  } catch (error) {
    console.error('更新问题状态失败:', error)
    ElMessage.error('更新问题状态失败，请重试')
  }
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

// 获取状态对应的标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    'pending': 'info',
    'processing': 'primary',
    'resolved': 'success',
    'closed': 'default'
  }
  return statusMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'resolved': '已解决',
    'closed': '已关闭'
  }
  return statusMap[status] || status
}

onMounted(() => {
  loadProblemsData()
})
</script>

<style scoped>
.management-container {
  max-width: 1400px;
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
  gap: 10px;
  align-items: center;
}

.filter-section {
  display: flex;
  align-items: center;
  padding: 20px 0;
  flex-wrap: wrap;
  gap: 10px;
}

.problems-table {
  margin-bottom: 20px;
}

.problem-summary {
  cursor: pointer;
  color: #409eff;
  text-decoration: underline;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}

.problem-detail {
  overflow-y: auto;
  max-height: 60vh;
}

.detail-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.detail-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #909399;
}

.detail-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item label {
  font-weight: bold;
  color: #606266;
}

.detail-content {
  margin-bottom: 20px;
}

.detail-content h4 {
  margin: 15px 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.detail-content p {
  margin: 0 0 10px 0;
  line-height: 1.6;
  color: #606266;
}

.entities {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 10px 0;
}

.entity-tag {
  display: inline-block;
  padding: 4px 12px;
  background-color: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 14px;
}

.feedback-examples {
  margin-top: 10px;
}

.detail-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
}
</style>