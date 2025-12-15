import requests

# 测试1：用户注册
print("=== 测试1：用户注册 ===")
response = requests.post(
    "http://localhost:8000/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    }
)
print(response.json())

# 测试2：用户登录
print("\n=== 测试2：用户登录 ===")
response = requests.post(
    "http://localhost:8000/login",
    json={
        "username": "testuser",
        "password": "123456"
    }
)
print(response.json())

# 测试3：错误的密码
print("\n=== 测试3：错误密码 ===")
response = requests.post(
    "http://localhost:8000/login",
    json={
        "username": "testuser",
        "password": "wrongpass"
    }
)
print(response.status_code, response.json())