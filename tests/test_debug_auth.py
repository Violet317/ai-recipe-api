import requests

print("=== 测试1：注册 ===")
response = requests.post(
    "http://localhost:8000/register",
    json={"username": "debug_user", "email": "debug@test.com", "password": "debug123"}
)
print(f"状态码: {response.status_code}")
print(f"原始响应: {response.text}")  # 不调用json()，避免解析错误

print("\n=== 测试2：登录 ===")
response = requests.post(
    "http://localhost:8000/login",
    json={"username": "debug_user", "password": "debug123"}
)
print(f"状态码: {response.status_code}")
print(f"原始响应: {response.text}")

print("\n=== 测试3：数据库验证 ===")
from models import SessionLocal, User
db = SessionLocal()
users = db.query(User).all()
print(f"数据库用户数量: {len(users)}")
for u in users:
    print(f"- ID: {u.id}, 用户名: {u.username}, 邮箱: {u.email}")
db.close()