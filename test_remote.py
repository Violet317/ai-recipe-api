import requests

# 替换为你的实际域名
API_BASE = "https://ai-recipe-api.up.railway.app"

print("=== 测试公网API ===")

# 测试推荐接口
print("\n1. 测试推荐接口")
response = requests.post(
    f"{API_BASE}/recommend",
    json={"ingredients": ["番茄", "鸡蛋"]}
)
print(response.json())

# 测试注册接口
print("\n2. 测试注册接口")
response = requests.post(
    f"{API_BASE}/register",
    json={"username": "testuser", "email": "test@example.com", "password": "test123"}
)
print(response.json())

# 测试登录接口
print("\n3. 测试登录接口")
response = requests.post(
    f"{API_BASE}/login",
    json={"username": "testuser", "password": "test123"}
)
print(response.json())