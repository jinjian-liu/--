from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化SQLAlchemy对象
db = SQLAlchemy()

# 定义Feedback模型 - 客户反馈表
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processed
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 与Problem的关系 - 一对多
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=True)
    problem = db.relationship('Problem', backref=db.backref('feedbacks', lazy=True))

# 定义Problem模型 - 问题表
class Problem(db.Model):
    __tablename__ = 'problems'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 技术问题, 服务态度, 价格异议, 功能建议, 其他
    severity = db.Column(db.String(20), nullable=False, default='中')  # 高, 中, 低
    feedback_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')  # pending, resolved
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 定义FeedbackExample模型 - 反馈示例表
class FeedbackExample(db.Model):
    __tablename__ = 'feedback_examples'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    
    # 与Problem的关系
    problem = db.relationship('Problem', backref=db.backref('feedback_examples', lazy=True))

# 定义AnalysisResult模型 - 分析结果表
class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_type = db.Column(db.String(50), nullable=False)  # typeDistribution, timeTrend, highFrequencyProblems, summary
    content = db.Column(db.Text, nullable=False)  # JSON格式的分析结果
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 数据库初始化函数
def init_db(app):
    # 配置数据库连接
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URI', 'mysql+pymysql://root:password@localhost/nlp_feedback')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    # 创建数据库表（如果不存在）
    with app.app_context():
        db.create_all()
        
        # 添加初始分析结果数据（如果不存在）
        if not AnalysisResult.query.filter_by(analysis_type='typeDistribution').first():
            # 问题类型分布
            type_distribution = AnalysisResult(
                analysis_type='typeDistribution',
                content="{\"labels\": [\"技术问题\", \"服务态度\", \"价格异议\", \"功能建议\", \"其他\"], \"values\": [45, 20, 15, 12, 8]}"
            )
            
            # 时间趋势
            time_trend = AnalysisResult(
                analysis_type='timeTrend',
                content="{\"dates\": [\"2025-08-01\", \"2025-08-02\", \"2025-08-03\", \"2025-08-04\", \"2025-08-05\", \"2025-08-06\", \"2025-08-07\"], \"counts\": [12, 19, 15, 28, 22, 31, 25]}"
            )
            
            # 高频问题
            high_freq_problems = AnalysisResult(
                analysis_type='highFrequencyProblems',
                content="[{\"rank\": 1, \"summary\": \"系统登录失败，提示账号或密码错误\", \"count\": 48, \"type\": \"技术问题\", \"severity\": \"高\"},{\"rank\": 2, \"summary\": \"客服响应时间过长\", \"count\": 36, \"type\": \"服务态度\", \"severity\": \"中\"},{\"rank\": 3, \"summary\": \"产品价格偏高，建议调整\", \"count\": 29, \"type\": \"价格异议\", \"severity\": \"中\"},{\"rank\": 4, \"summary\": \"希望增加数据导出功能\", \"count\": 24, \"type\": \"功能建议\", \"severity\": \"低\"},{\"rank\": 5, \"summary\": \"页面加载速度慢\", \"count\": 21, \"type\": \"技术问题\", \"severity\": \"中\"},{\"rank\": 6, \"summary\": \"操作界面不够友好\", \"count\": 18, \"type\": \"技术问题\", \"severity\": \"低\"},{\"rank\": 7, \"summary\": \"退款流程复杂\", \"count\": 15, \"type\": \"服务态度\", \"severity\": \"中\"},{\"rank\": 8, \"summary\": \"希望支持多语言\", \"count\": 12, \"type\": \"功能建议\", \"severity\": \"低\"},{\"rank\": 9, \"summary\": \"报表数据不准确\", \"count\": 10, \"type\": \"技术问题\", \"severity\": \"高\"},{\"rank\": 10, \"summary\": \"希望增加移动端适配\", \"count\": 8, \"type\": \"功能建议\", \"severity\": \"低\"}]"
            )
            
            # 分析总结
            summary = AnalysisResult(
                analysis_type='summary',
                content="<p>根据最近一周的客户反馈分析，主要问题集中在技术问题（45%）和服务态度（20%）两个方面。</p><p><strong>技术问题</strong>主要包括系统登录失败、页面加载速度慢和操作界面不够友好等，这些问题严重影响了用户体验，建议技术团队优先解决。</p><p><strong>服务态度</strong>方面，客服响应时间过长和退款流程复杂是用户反映较多的问题，建议优化客服流程和退款机制。</p><p><strong>价格异议</strong>占比15%，反映了部分用户对产品价格的顾虑，建议评估市场竞争力，考虑适当调整价格策略。</p><p><strong>功能建议</strong>占比12%，用户希望增加数据导出、多语言支持和移动端适配等功能，这些建议可纳入产品 roadmap 考虑。</p>"
            )
            
            db.session.add_all([type_distribution, time_trend, high_freq_problems, summary])
            db.session.commit()