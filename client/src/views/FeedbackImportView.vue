<template>
  <div class="import-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入客户反馈数据</span>
        </div>
      </template>
      
      <div class="import-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="文本导入" name="text">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="请输入或粘贴客户反馈内容，每行一条反馈"
              v-model="textFeedback"
              style="margin-bottom: 20px;"
            />
            <el-button type="primary" @click="importTextFeedback">
              <el-icon><UploadFilled /></el-icon>
              导入文本反馈
            </el-button>
          </el-tab-pane>
          
          <el-tab-pane label="文件导入" name="file">
            <div class="file-upload">
              <el-upload
                ref="upload"
                class="upload-demo"
                action=""
                :auto-upload="false"
                :before-upload="handleBeforeUpload"
                :on-change="handleFileChange"
                :file-list="fileList"
                :on-remove="handleRemove"
              >
                <el-button type="primary">
                  <el-icon><UploadFilled /></el-icon>
                  选择文件
                </el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持上传txt、csv文件，单个文件不超过10MB
                  </div>
                </template>
              </el-upload>
              <el-button 
                type="success" 
                @click="importFileFeedback"
                :disabled="fileList.length === 0"
                style="margin-top: 20px;"
              >
                开始导入
              </el-button>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="图片识别" name="image">
            <div class="image-upload">
              <el-upload
                ref="imageUpload"
                class="upload-demo"
                action=""
                :auto-upload="false"
                :on-change="handleImageChange"
                :file-list="imageList"
                :on-remove="handleImageRemove"
                accept="image/*"
              >
                <el-button type="primary">
                  <el-icon><UploadFilled /></el-icon>
                  选择图片
                </el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持上传JPG、PNG格式的图片，单个图片不超过5MB
                  </div>
                </template>
              </el-upload>
              <el-button 
                type="success" 
                @click="importImageFeedback"
                :disabled="imageList.length === 0"
                style="margin-top: 20px;"
              >
                开始识别并导入
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
    
    <!-- 导入结果对话框 -->
    <el-dialog v-model="resultDialogVisible" title="导入结果" width="50%">
      <div class="result-content">
        <div class="result-status" :class="importSuccess ? 'success' : 'error'">
          {{ importSuccess ? '导入成功' : '导入失败' }}
        </div>
        <div class="result-message" v-if="importMessage">
          {{ importMessage }}
        </div>
        <div class="result-stats" v-if="importSuccess && importStats">
          <p>导入反馈总数：{{ importStats.total }}</p>
          <p>成功处理：{{ importStats.success }}</p>
          <p>处理失败：{{ importStats.failed }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resultDialogVisible = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const activeTab = ref('text')
const textFeedback = ref('')
const fileList = ref([])
const imageList = ref([])
const resultDialogVisible = ref(false)
const importSuccess = ref(false)
const importMessage = ref('')
const importStats = ref(null)

// 处理文件上传前的校验
const handleBeforeUpload = (file) => {
  const isTxtOrCsv = file.type === 'text/plain' || file.type === 'text/csv'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isTxtOrCsv) {
    ElMessage.error('仅支持txt、csv格式文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }
  return true
}

// 处理文件变化
const handleFileChange = (file, newFileList) => {
  fileList.value = newFileList
}

// 处理文件移除
const handleRemove = (file, newFileList) => {
  fileList.value = newFileList
}

// 处理图片变化
const handleImageChange = (file, newFileList) => {
  imageList.value = newFileList
}

// 处理图片移除
const handleImageRemove = (file, newFileList) => {
  imageList.value = newFileList
}

// 导入文本反馈
const importTextFeedback = async () => {
  if (!textFeedback.value.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }

  try {
    const response = await axios.post('/api/feedback/import/text', {
      content: textFeedback.value
    })
    showImportResult(true, response.data)
  } catch (error) {
    showImportResult(false, error.response?.data || { message: '导入失败，请重试' })
  }
}

// 导入文件反馈
const importFileFeedback = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  const formData = new FormData()
  formData.append('file', fileList.value[0].raw)

  try {
    const response = await axios.post('/api/feedback/import/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    showImportResult(true, response.data)
  } catch (error) {
    showImportResult(false, error.response?.data || { message: '导入失败，请重试' })
  }
}

// 导入图片识别反馈
const importImageFeedback = async () => {
  if (imageList.value.length === 0) {
    ElMessage.warning('请选择图片')
    return
  }

  const formData = new FormData()
  formData.append('image', imageList.value[0].raw)

  try {
    const response = await axios.post('/api/feedback/import/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    showImportResult(true, response.data)
  } catch (error) {
    showImportResult(false, error.response?.data || { message: '图片识别失败，请重试' })
  }
}

// 显示导入结果
const showImportResult = (success, data) => {
  importSuccess.value = success
  importMessage.value = data.message || ''
  importStats.value = data.stats || null
  resultDialogVisible.value = true
}
</script>

<style scoped>
.import-container {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-content {
  padding: 20px 0;
}

.file-upload,
.image-upload {
  display: flex;
  flex-direction: column;
}

.result-content {
  padding: 20px;
}

.result-status {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
}

.result-status.success {
  color: #67c23a;
}

.result-status.error {
  color: #f56c6c;
}

.result-message {
  color: #606266;
  margin-bottom: 15px;
  text-align: center;
}

.result-stats {
  background-color: #f0f2f5;
  padding: 15px;
  border-radius: 4px;
}

.result-stats p {
  margin: 5px 0;
  color: #606266;
}
</style>