# 基于NLP的客户问题反馈分析与管理系统

## 项目概述
本系统利用自然语言处理技术，自动分析客户反馈，提炼关键信息，将相似问题聚类，并提供可视化分析与管理功能，帮助企业高效响应客户需求，优化产品与服务。

## 技术栈

### 前端
- Vue 3
- Element Plus
- ECharts
- Vite

### 后端
- Python
- Flask
- Flask-SQLAlchemy
- MySQL
- DeepSeek API集成

## 快速开始

### 环境要求
- Node.js (v16+) 
- Python (v3.8+) 
- MySQL 8.0+

### 后端设置

1. 进入server目录
```bash
cd server
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置MySQL数据库

   a. 确保MySQL服务已启动
   b. 使用提供的初始化脚本创建数据库和表结构：
   ```bash
   mysql -u root -p < init_database.sql
   ```
   c. 修改`.env`文件中的数据库连接配置：
   ```env
   # 替换为你的MySQL用户名、密码
   DATABASE_URI=mysql+pymysql://root:your_password@localhost/nlp_feedback
   ```

4. 配置DeepSeek API

   在`.env`文件中配置DeepSeek API密钥：
   ```env
   # 替换为你的DeepSeek API密钥
   LLM_API_KEY=your-deepseek-api-key
   # DeepSeek API端点已默认配置
   # LLM_API_URL=https://api.deepseek.com/v1/chat/completions
   ```

5. 启动后端服务器
```bash
python app.py
```
后端服务将运行在 http://localhost:5000

### 前端设置

1. 进入client目录
```bash
cd client
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```
前端服务将运行在 http://localhost:3001

## 主要功能

1. **数据导入与预处理**
   - 支持文本导入
   - 支持文件导入（txt、csv）
   - 支持图片识别（模拟实现）

2. **关键信息提取**
   - 自动生成问题摘要
   - 识别问题类型

3. **问题分类与聚类**
   - 基于关键词的问题分类
   - 简单的相似问题聚类

4. **分析与可视化**
   - 问题类型分布图表
   - 反馈数量时间趋势
   - 高频问题列表
   - 分析总结报告

5. **管理与协作**
   - 问题列表查看与搜索
   - 问题状态更新
   - 问题详情查看

## 注意事项

1. 系统已配置使用MySQL数据库进行持久化存储，确保正确配置数据库连接信息。

2. LLM API已集成DeepSeek API，使用前需要配置有效的API密钥。

3. 图片识别功能目前为模拟实现，实际使用时可以集成OCR服务。

4. 在生产环境中使用时，建议：
   - 将`.env`文件中的`DEBUG`设置为`False`
   - 使用Gunicorn等WSGI服务器运行后端应用
   - 配置合适的数据库权限和API密钥保护措施

5. 系统包含了示例数据，可用于测试和演示目的。

## 项目结构

```
├── client/           # 前端项目目录
│   ├── src/          # 前端源代码
│   │   ├── views/    # 页面组件
│   │   ├── router/   # 路由配置
│   │   ├── main.js   # 入口文件
│   │   └── App.vue   # 根组件
│   ├── package.json  # 前端依赖配置
│   └── vite.config.js # Vite配置
├── server/           # 后端项目目录
│   ├── routes/       # API路由
│   ├── app.py        # 后端入口
│   └── requirements.txt # 后端依赖
└── README.md         # 项目说明文档
```

## 部署指南

### 前端构建
```bash
cd client
npm run build
```
构建后的文件将生成在 `client/dist` 目录下，可以部署到任何静态文件服务器。

### 后端部署
在生产环境中，建议使用Gunicorn或uWSGI等WSGI服务器来运行Flask应用：
```bash
pip install gunicorn
cd server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 开发说明

1. 前端开发时，所有API请求都会通过Vite的代理转发到后端服务器。

2. 后端使用Blueprint组织路由，便于扩展和维护。

3. 在实际项目中，建议添加更完善的错误处理、日志记录和安全措施。

4. 数据模型和存储方式可以根据实际需求进行调整。