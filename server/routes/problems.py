from flask import Blueprint, request, jsonify
from app import app
from database import db, Problem, FeedbackExample
from datetime import datetime

# 创建蓝图
problems_bp = Blueprint('problems', __name__)

# 获取问题列表
@problems_bp.route('/api/problems/list', methods=['GET'])
def get_problems_list():
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        problem_type = request.args.get('type', '')
        severity = request.args.get('severity', '')
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        
        with app.app_context():
            # 构建查询
            query = Problem.query
            
            # 按关键词过滤
            if keyword:
                query = query.filter(
                    (Problem.summary.like(f'%{keyword}%')) | 
                    (Problem.description.like(f'%{keyword}%'))
                )
            
            # 按问题类型过滤
            if problem_type:
                # 注意：前端传递的是英文类型，这里需要映射到中文类型
                type_map = {
                    'technical': '技术问题',
                    'service': '服务态度',
                    'price': '价格异议',
                    'feature': '功能建议',
                    'other': '其他'
                }
                chinese_type = type_map.get(problem_type, problem_type)
                query = query.filter(Problem.type == chinese_type)
            
            # 按严重程度过滤
            if severity:
                # 前端传递的是英文严重程度，这里需要映射到中文
                severity_map = {
                    'high': '高',
                    'medium': '中',
                    'low': '低'
                }
                chinese_severity = severity_map.get(severity, severity)
                query = query.filter(Problem.severity == chinese_severity)
            
            # 按状态过滤
            if status:
                query = query.filter(Problem.status == status)
            
            # 计算总数量
            total = query.count()
            
            # 分页
            paginated_problems = query.offset((page - 1) * page_size).limit(page_size).all()
            
            # 转换为字典列表
            items = []
            for problem in paginated_problems:
                # 查询反馈示例
                feedback_examples = FeedbackExample.query.filter_by(problem_id=problem.id).limit(5).all()
                
                items.append({
                    'id': problem.id,
                    'summary': problem.summary,
                    'description': problem.description,
                    'type': problem.type,
                    'severity': problem.severity,
                    'feedbackCount': problem.feedback_count,
                    'status': problem.status,
                    'createTime': problem.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'updateTime': problem.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'entities': [],  # 实体识别结果
                    'feedbackExamples': [example.content for example in feedback_examples]
                })
            
            return jsonify({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 获取问题详情
@problems_bp.route('/api/problems/<int:problem_id>', methods=['GET'])
def get_problem_detail(problem_id):
    try:
        with app.app_context():
            # 查找问题
            problem = Problem.query.get(problem_id)
            
            if not problem:
                return jsonify({'success': False, 'message': '问题不存在'}), 404
            
            # 查询反馈示例
            feedback_examples = FeedbackExample.query.filter_by(problem_id=problem.id).all()
            
            # 构建返回结果
            result = {
                'id': problem.id,
                'summary': problem.summary,
                'description': problem.description,
                'type': problem.type,
                'severity': problem.severity,
                'feedbackCount': problem.feedback_count,
                'status': problem.status,
                'createTime': problem.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'updateTime': problem.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'entities': [],  # 实体识别结果
                'feedbackExamples': [example.content for example in feedback_examples]
            }
            
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 标记问题为已解决
@problems_bp.route('/api/problems/<int:problem_id>/resolve', methods=['POST'])
def resolve_problem(problem_id):
    try:
        with app.app_context():
            # 查找问题
            problem = Problem.query.get(problem_id)
            
            if not problem:
                return jsonify({'success': False, 'message': '问题不存在'}), 404
            
            # 更新问题状态
            problem.status = 'resolved'
            problem.update_time = datetime.now()
            
            # 提交更改
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '问题已标记为已解决'
            })
    except Exception as e:
        # 发生错误时回滚
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 更新问题状态
@problems_bp.route('/api/problems/<int:problem_id>/update-status', methods=['POST'])
def update_problem_status(problem_id):
    try:
        with app.app_context():
            # 查找问题
            problem = Problem.query.get(problem_id)
            
            if not problem:
                return jsonify({'success': False, 'message': '问题不存在'}), 404
            
            # 获取新状态
            data = request.json
            new_status = data.get('status', '')
            
            if not new_status:
                return jsonify({'success': False, 'message': '请提供新的状态'}), 400
            
            # 检查状态是否有效
            valid_statuses = ['pending', 'processing', 'resolved', 'closed']
            if new_status not in valid_statuses:
                return jsonify({'success': False, 'message': '无效的状态值'}), 400
            
            # 更新问题状态
            problem.status = new_status
            problem.update_time = datetime.now()
            
            # 提交更改
            db.session.commit()
            
            return jsonify({'success': True, 'message': '问题状态已更新'})
    except Exception as e:
        # 发生错误时回滚
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 注册蓝图
def register_routes():
    app.register_blueprint(problems_bp)

# 自动注册路由
register_routes()