import os
import requests
import json
from app import app

class LLMInterface:
    """
    大语言模型接口封装类，负责处理与大模型的交互和输出格式管理
    """
    
    def __init__(self):
        # 从配置中获取API密钥和URL
        self.api_key = app.config.get('LLM_API_KEY', '')
        self.api_url = app.config.get('LLM_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        # 设置请求头 - DeepSeek API使用Bearer认证
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
    def call_llm(self, messages, model='deepseek-chat', temperature=0.7, max_tokens=1000):
        """
        调用DeepSeek大模型API
        
        参数:
            messages: 消息列表，格式为[{"role": "user", "content": "用户输入"}, ...]
            model: 模型名称，DeepSeek默认为'deepseek-chat'
            temperature: 温度参数
            max_tokens: 最大 tokens 数
        
        返回:
            大模型的回复内容，如果调用失败则返回None
        """
        try:
            # 构建请求体 - DeepSeek API与OpenAI API参数格式类似
            payload = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            else:
                print(f"DeepSeek API调用失败: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"DeepSeek API调用异常: {str(e)}")
            return None

    def analyze_feedback(self, feedback_text):
        """
        分析客户反馈，提取问题类型、摘要等信息
        
        参数:
            feedback_text: 客户反馈文本
        
        返回:
            分析结果字典，包含问题类型、摘要、严重程度等信息
        """
        # 构建提示词
        prompt = f"""请分析以下客户反馈，提取相关信息：
        客户反馈：{feedback_text}
        
        请按照以下JSON格式返回分析结果：
        {{
            "type": "问题类型",
            "summary": "问题摘要",
            "severity": "严重程度",
            "entities": ["实体列表"],
            "sentiment": "情感倾向"
        }}
        
        问题类型选项：技术问题、服务态度、价格异议、功能建议、其他
        严重程度选项：高、中、低
        情感倾向选项：正面、中性、负面
        """
        
        messages = [
            {"role": "system", "content": "你是一个客户反馈分析助手，擅长分析客户反馈内容并提取关键信息。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用大模型
        response = self.call_llm(messages, temperature=0.5)
        
        if response and 'choices' in response and len(response['choices']) > 0:
            # 解析DeepSeek的回复
            try:
                result_text = response['choices'][0]['message']['content']
                # 提取JSON部分
                if '{' in result_text and '}' in result_text:
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    result_json = json.loads(result_text[json_start:json_end])
                    return result_json
                # 如果没有JSON格式，尝试直接解析
                return json.loads(result_text)
            except json.JSONDecodeError:
                print(f"LLM输出解析失败: {result_text}")
                # 返回默认的模拟分析结果
                return self._get_default_analysis(feedback_text)
        
        # 如果调用失败，返回默认的模拟分析结果
        return self._get_default_analysis(feedback_text)
    
    def generate_summary(self, text):
        """
        生成文本摘要
        
        参数:
            text: 要摘要的文本
        
        返回:
            文本摘要
        """
        # 构建提示词
        prompt = f"""请为以下文本生成简洁的摘要，不超过50个字符：
        {text}
        """
        
        messages = [
            {"role": "system", "content": "你是一个文本摘要助手，擅长生成简洁的文本摘要。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用大模型
        response = self.call_llm(messages, temperature=0.3, max_tokens=100)
        
        if response and 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content'].strip()
        
        # 如果调用失败，返回默认的模拟摘要
        if len(text) <= 50:
            return text
        return text[:50] + '...'
    
    def find_similar_problems(self, summary, existing_problems):
        """
        查找相似问题
        
        参数:
            summary: 问题摘要
            existing_problems: 现有问题列表
        
        返回:
            最相似的问题，如果没有找到则返回None
        """
        # 如果没有问题，直接返回None
        if not existing_problems:
            return None
        
        # 在实际应用中，这里应该调用大模型进行语义相似度计算
        # 这里使用简单的关键词匹配作为模拟实现
        for problem in existing_problems:
            # 检查是否有共同的关键词
            problem_words = set(problem.summary.lower())
            summary_words = set(summary.lower())
            # 如果有超过3个共同字符，认为是类似问题
            if len(problem_words.intersection(summary_words)) > 3:
                return problem
        
        return None
    
    def _get_default_analysis(self, feedback_text):
        """
        获取默认的模拟分析结果
        
        参数:
            feedback_text: 客户反馈文本
        
        返回:
            默认的分析结果字典
        """
        # 示例：根据关键词判断问题类型
        problem_type = '其他'
        if '登录' in feedback_text or '账号' in feedback_text or '密码' in feedback_text:
            problem_type = '技术问题'
        elif '客服' in feedback_text or '服务' in feedback_text or '响应' in feedback_text:
            problem_type = '服务态度'
        elif '价格' in feedback_text or '收费' in feedback_text or '贵' in feedback_text:
            problem_type = '价格异议'
        elif '功能' in feedback_text or '建议' in feedback_text or '希望' in feedback_text:
            problem_type = '功能建议'
        
        # 默认严重程度
        severity = '中'
        if '无法' in feedback_text or '不能' in feedback_text or '失败' in feedback_text:
            severity = '高'
        
        # 默认情感倾向
        sentiment = '中性'
        if '满意' in feedback_text or '很好' in feedback_text or '不错' in feedback_text:
            sentiment = '正面'
        elif '不满意' in feedback_text or '糟糕' in feedback_text or '差' in feedback_text:
            sentiment = '负面'
        
        return {
            'type': problem_type,
            'summary': self.generate_summary(feedback_text),
            'severity': severity,
            'entities': [],
            'sentiment': sentiment
        }

# 创建全局的LLM接口实例
llm_interface = LLMInterface()