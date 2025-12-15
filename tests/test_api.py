import requests

# 测试场景1：普通用户
print("=== 测试1：普通用户 ===")
response = requests.post(
    "http://localhost:8000/recommend",
    json={"ingredients": ["番茄", "鸡蛋", "挂面"]}
)
print(response.json())
print()

# 测试场景2：健身人群
print("=== 测试2：健身人群（低脂） ===")
response = requests.post(
    "http://localhost:8000/recommend",
    json={"ingredients": ["鸡胸肉", "生菜"], "tags": ["低脂"]}
)
print(response.json())
print()

# 测试场景3：过敏人群
print("=== 测试3：过敏人群 ===")
response = requests.post(
    "http://localhost:8000/recommend",
    json={"ingredients": ["南瓜", "藜麦"], "tags": ["过敏友好"]}
)
print(response.json())

# 测试场景4：时间紧张的用户
print("=== 测试4：30分钟内能做的 ===")
response = requests.post(
    "http://localhost:8000/recommend",
    json={"ingredients": ["鸡蛋", "番茄"], "tags": ["快手"]}
)
print(response.json())