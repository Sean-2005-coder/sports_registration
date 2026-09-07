# 合二为一，注意修改greet.html和index.html的表单提交地址


from flask import Flask,render_template,request # 导入渲染 HTML 文件的函数
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 假设表单已经提交
        # 处理 POST 请求
        name = request.form.get('name','world')  # 获取表单数据中的 name 值
        return render_template('greet.html', name=name)  # 渲染 greet.html 模板
    elif request.method == 'GET':
        # 处理 GET 请求
        return render_template('index.html')  # 渲染 index.html 模板
