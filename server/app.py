from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['LLM_API_KEY'] = os.environ.get('LLM_API_KEY', '')
app.config['LLM_API_URL'] = os.environ.get('LLM_API_URL', 'https://api.example.com/v1/chat/completions')

# 配置MySQL数据库连接
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI', 'mysql+pymysql://root:password@localhost/nlp_feedback')

# 导入数据库配置
from database import db, init_db

# 初始化数据库
init_db(app)

# 导入路由
from routes import *

if __name__ == '__main__':
    # 在开发环境中运行，生产环境应使用WSGI服务器
    app.run(debug=True, host='0.0.0.0', port=5000)