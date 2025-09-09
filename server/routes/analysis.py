from flask import Blueprint, request, jsonify
from app import app
from database import db, AnalysisResult
import json
from datetime import datetime

# 创建蓝图
analysis_bp = Blueprint('analysis', __name__)

# 获取分析报告
@analysis_bp.route('/api/analysis/report', methods=['GET'])
def get_analysis_report():
    try:
        # 获取查询参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        with app.app_context():
            # 构建查询条件
            query = AnalysisResult.query
            
            # 如果有日期参数，添加日期过滤
            if start_date and end_date:
                try:
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(AnalysisResult.start_date >= start_date_obj, AnalysisResult.end_date <= end_date_obj)
                except ValueError:
                    # 如果日期格式不正确，使用默认数据
                    pass
            
            # 查询所有分析结果
            results = query.all()
            
            # 构建返回结果
            analysis_report = {}
            for result in results:
                if result.analysis_type == 'summary':
                    # 摘要直接使用文本
                    analysis_report[result.analysis_type] = result.content
                else:
                    # 其他类型解析JSON
                    try:
                        analysis_report[result.analysis_type] = json.loads(result.content)
                    except json.JSONDecodeError:
                        # 如果JSON解析失败，使用空字典
                        analysis_report[result.analysis_type] = {}
            
            return jsonify(analysis_report)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 注册蓝图
def register_routes():
    app.register_blueprint(analysis_bp)

# 自动注册路由
register_routes()