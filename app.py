from flask import Flask, render_template, request, jsonify, session
from crawler import WechatCrawler
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 设置session密钥
crawler = WechatCrawler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_cookie', methods=['POST'])
def get_cookie():
    url = request.form.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': '请输入URL'})
    
    try:
        result = crawler.get_cookie(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_articles', methods=['POST'])
def get_articles():
    url = request.form.get('url')
    cookie = request.form.get('cookie')
    
    if not url or not cookie:
        return jsonify({'status': 'error', 'message': '请输入URL和Cookie'})
    
    try:
        # 保存cookie到session
        session['cookie'] = cookie
        
        # 获取文章列表
        articles = crawler.get_history_articles(url, cookie)
        
        # 格式化时间
        for article in articles:
            if article['create_time']:
                timestamp = int(article['create_time'])
                article['create_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'status': 'success',
            'message': f'成功获取 {len(articles)} 篇文章',
            'articles': articles
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)