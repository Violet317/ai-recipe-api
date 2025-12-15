import requests

# 测试注册接口是否可达
print("=== 测试注册接口可达性 ===")
try:
    response = requests.post(
        "http://localhost:8000/register",
        json={"username": "test", "email": "test@test.com", "password": "test"},
        timeout=5
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}")  # 只显示前200字符
except Exception as e:
    print(f"连接错误: {e}")

# 测试登录接口
print("\n=== 测试登录接口可达性 ===")
try:
    response = requests.post(
        "http://localhost:8000/login",
        json={"username": "test", "password": "test"},
        timeout=5
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}")
except Exception as e:
    print(f"连接错误: {e}")