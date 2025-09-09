from flask import Blueprint, jsonify
from app import app
from database import db, Feedback, Problem

# 创建蓝图
dashboard_bp = Blueprint('dashboard', __name__)

# 获取仪表盘统计数据
@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    with app.app_context():
        # 从数据库查询统计数据
        total_feedbacks = Feedback.query.count()
        pending_problems = Problem.query.filter_by(status='pending').count()
        resolved_problems = Problem.query.filter_by(status='resolved').count()
        
        stats = {
            'totalFeedbacks': total_feedbacks,
            'pendingProblems': pending_problems,
            'resolvedProblems': resolved_problems
        }
        return jsonify(stats)

# 注册蓝图
def register_routes():
    app.register_blueprint(dashboard_bp)

# 自动注册路由
register_routes()