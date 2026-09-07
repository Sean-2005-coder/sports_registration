# Flask 体育项目报名系统

这是一个 Flask 注册、登录和体育项目报名展示程序。

## 本地运行

```powershell
\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "change-this-secret"
python app.py
```

打开 http://127.0.0.1:5000 。

## 页面流程

1. `/`：登录
2. `/register`：注册并选择体育项目、性别
3. `/profile`：查看当前用户信息
4. `/registrants`：查看所有用户报名的体育项目和性别

数据库和会话文件只在本地运行时生成，不提交到公开仓库。