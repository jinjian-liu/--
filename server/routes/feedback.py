from flask import Blueprint, request, jsonify
import os
from app import app
from database import db, Feedback, Problem, FeedbackExample
from datetime import datetime
# 导入新创建的LLM接口
from llm_interface import llm_interface

# 创建蓝图
feedback_bp = Blueprint('feedback', __name__)

# 导入文本反馈
@feedback_bp.route('/api/feedback/import/text', methods=['POST'])
def import_text_feedback():
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'message': '请输入反馈内容'}), 400
        
        # 分割文本内容为多行
        feedbacks = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 处理每条反馈
        processed_count = 0
        failed_count = 0
        
        with app.app_context():
            for feedback in feedbacks:
                try:
                    # 处理反馈
                    process_feedback(feedback)
                    processed_count += 1
                except Exception as e:
                    print(f'处理反馈失败: {e}')
                    failed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {len(feedbacks)} 条反馈',
            'stats': {
                'total': len(feedbacks),
                'success': processed_count,
                'failed': failed_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 导入文件反馈
@feedback_bp.route('/api/feedback/import/file', methods=['POST'])
def import_file_feedback():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择文件'}), 400
        
        # 读取文件内容
        content = file.read().decode('utf-8')
        
        # 分割文件内容为多行
        feedbacks = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 处理每条反馈
        processed_count = 0
        failed_count = 0
        
        with app.app_context():
            for feedback in feedbacks:
                try:
                    process_feedback(feedback)
                    processed_count += 1
                except Exception as e:
                    print(f'处理反馈失败: {e}')
                    failed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {len(feedbacks)} 条反馈',
            'stats': {
                'total': len(feedbacks),
                'success': processed_count,
                'failed': failed_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 导入图片识别反馈
@feedback_bp.route('/api/feedback/import/image', methods=['POST'])
def import_image_feedback():
    try:
        # 检查是否有图片上传
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '请选择图片'}), 400
        
        image = request.files['image']
        
        # 检查文件名
        if image.filename == '':
            return jsonify({'success': False, 'message': '请选择图片'}), 400
        
        # 在实际应用中，这里应该调用OCR服务识别图片中的文字
        # 这里使用模拟数据
        recognized_text = "这是模拟的图片识别结果，客户反馈系统登录困难，希望能够优化登录流程。"
        
        # 处理识别到的文本
        with app.app_context():
            process_feedback(recognized_text)
        
        return jsonify({
            'success': True,
            'message': '图片识别并导入成功',
            'stats': {
                'total': 1,
                'success': 1,
                'failed': 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 处理单条反馈的函数
def process_feedback(feedback_text):
    # 构建反馈对象
    feedback = Feedback(
        content=feedback_text,
        status='pending',
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    
    # 添加到数据库
    db.session.add(feedback)
    
    # 使用LLM接口分析反馈
    analysis_result = llm_interface.analyze_feedback(feedback_text)
    
    # 从分析结果中提取信息
    problem_type = analysis_result.get('type', '其他')
    summary = analysis_result.get('summary', '')
    severity = analysis_result.get('severity', '中')
    
    # 查询所有现有问题
    existing_problems = Problem.query.all()
    
    # 检查是否已有类似问题
    similar_problem = llm_interface.find_similar_problems(summary, existing_problems)
    
    if similar_problem:
        # 如果有类似问题，增加反馈次数
        similar_problem.feedback_count += 1
        similar_problem.update_time = datetime.now()
        
        # 添加反馈示例
        feedback_example = FeedbackExample(
            problem_id=similar_problem.id,
            content=feedback_text,
            create_time=datetime.now()
        )
        db.session.add(feedback_example)
        
        # 关联反馈到问题
        feedback.problem_id = similar_problem.id
    else:
        # 如果没有类似问题，创建新问题
        problem = Problem(
            summary=summary,
            description=feedback_text,
            type=problem_type,
            severity=severity,
            feedback_count=1,
            status='pending',
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.session.add(problem)
        db.session.flush()  # 获取problem.id
        
        # 添加反馈示例
        feedback_example = FeedbackExample(
            problem_id=problem.id,
            content=feedback_text,
            create_time=datetime.now()
        )
        db.session.add(feedback_example)
        
        # 关联反馈到问题
        feedback.problem_id = problem.id
    
    # 提交更改
    db.session.commit()

# 注册蓝图
def register_routes():
    app.register_blueprint(feedback_bp)

# 自动注册路由
register_routes()