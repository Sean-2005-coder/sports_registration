import sqlite3
import os
from pathlib import Path # 导入 Path 类，用于处理文件路径

from flask import Flask, render_template, request, redirect, session, url_for # 导入 Flask 类、渲染模板函数、请求对象、重定向函数、会话对象和 URL 生成函数
from werkzeug.security import generate_password_hash # 导入生成密码哈希的函数
from werkzeug.security import check_password_hash # 导入检查密码哈希的函数
from flask_session import Session # 导入 Flask-Session 扩展，用于在服务器端存储会话数据 ,制作 cookie  session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-only-secret-key')
app.config['SESSION_PERMANENT'] = False      #   配置会话是否永久有效
app.config['SESSION_TYPE'] = 'filesystem'  # 配置会话类型为文件系统
Session(app)  # 初始化 Flask-Session

DATABASE = Path(app.root_path) / 'register.db'


def get_db(): # 获取数据库连接函数
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row  # 设置行工厂，使查询结果以字典形式返回
    return connection


def init_db():    # 初始化数据库函数     <th>ID</th># 定义一个自增的主键 id
    with get_db() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS registrants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                sport TEXT NOT NULL,
                gender TEXT NOT NULL
            )
        ''')


init_db()

#  REGISTER={}      #定义一个空字典，用于存储注册信息
SPORTS = ['baseball', 'basketball', 'badminton', 'pingpong']  # 定义一个包含运动选项的列表
GENDERS = ['Male', 'Female', 'Other']  # 定义一个包含性别选项的列表

# request.args.get()  只能读取网址：？...=.... 方法用于获取 URL 参数中的值。它接受两个参数：第一个参数是要获取的参数名，第二个参数是默认值（如果参数不存在时使用）。如果 URL 中没有提供该参数，则返回默认值。
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',name=session.get('registrant_id'))  # 渲染 index.html 模板，并传递注册用户的 ID（如果存在）作为参数



# GET 数据放在URL里面，提交完能看到    args
# POST 数据放在请求体里面，提交完看不到 form   
# request.form.get() 只能读取表单数据，不能读取 URL 参数中的值。
# request.args.get() 只能读取 URL 参数中的值，不能读取表单数据。它接受两个参数：第一个参数是要获取的参数名，第二个参数是默认值（如果参数不存在时使用）。如果 URL 中没有提供该参数，则返回默认值。

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', sports=SPORTS, genders=GENDERS)

    if not request.form:  # 检查是否有表单数据
        return "No form data received", 400  # 如果没有表单数据，返回错误信息和状态码 400
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    selected_sports = request.form.getlist('sport')
    gender = request.form.get('gender')

    if not selected_sports or any(sport not in SPORTS for sport in selected_sports):
        return "Invalid sport selected", 400

    selected_sports = list(dict.fromkeys(selected_sports))
    sport = ', '.join(selected_sports)

    if gender not in GENDERS:  # 检查所选性别是否在预定义的性别列表中
        return "Invalid gender selected", 400  # 如果所选性别无效，返回错误信息和状态码 400

#  将注册信息存储在 REGISTER 字典中
#    REGISTER['username'] = username
#   REGISTER['email'] = email
#    REGISTER['password'] = password
#    REGISTER['sport'] = sport
#    REGISTER['gender'] = gender



#   将注册信息存储在 SQLite 数据库中
    with get_db() as connection:
        connection.execute(
            '''INSERT INTO registrants (username, email, password, sport, gender)
               VALUES (?, ?, ?, ?, ?)''',
            (username, email, generate_password_hash(password), sport, gender)
        )

    return render_template(
        'register.html',
        registered=True,
        username=username,
        sports=SPORTS,
        genders=GENDERS
    )


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    with get_db() as connection:
        registrant = connection.execute(
            'SELECT * FROM registrants WHERE username = ? AND email = ? LIMIT 1',
            (username, email)
        ).fetchone()

    if registrant is None or not check_password_hash(registrant['password'], password):
        return render_template('index.html', error='用户名、邮箱或密码错误'), 401

    session['registrant_id'] = registrant['id']
    return redirect(url_for('profile'))


@app.route('/profile', methods=['GET'])
def profile():
    registrant_id = session.get('registrant_id')
    if registrant_id is None:
        return redirect(url_for('index'))

    with get_db() as connection:
        registrant = connection.execute(
            'SELECT username, email, sport, gender FROM registrants WHERE id = ?',
            (registrant_id,)
        ).fetchone()

    if registrant is None:
        session.clear()
        return redirect(url_for('index'))

    return render_template('greet.html', registrant=registrant)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/registrants', methods=['GET'])
def registrants():
    with get_db() as connection:
        registrants = connection.execute(
            'SELECT id, username, email, sport, gender FROM registrants ORDER BY id DESC'
        ).fetchall()
    return render_template('registrants.html', registrants=registrants)


@app.route('/deregistrant/<int:registrant_id>', methods=['POST']) # 定义一个路由，用于处理注销注册用户的请求，使用 POST 方法，并接受一个整数类型的参数 registrant_id（自己定义）
def deregistrant(registrant_id):
    with get_db() as connection:
        connection.execute(
            'DELETE FROM registrants WHERE id = ?',(registrant_id,)
        )
    return redirect('/registrants')             


if __name__ == '__main__':
    app.run(debug=True)  # 启动 Flask 应用，开启调试模式