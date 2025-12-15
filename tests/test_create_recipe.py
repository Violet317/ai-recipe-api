# test_create_recipe.py - 测试创建菜谱
import requests

# 测试创建新菜谱
print("=== 测试：创建新菜谱 ===")
response = requests.post(
    "http://localhost:8000/recipes",
    json={
        "name": "蒜蓉西兰花",
        "ingredients": ["西兰花", "蒜蓉", "盐"],
        "steps": ["焯水", "炒蒜蓉", "翻炒"],
        "time": 15,
        "tags": ["快手", "素食"]
    }
)

print(f"状态码: {response.status_code}")
print(f"返回内容: {response.json()}")

# 验证数据库是否新增
if response.status_code == 200:
    print("\n✅ 创建成功！")
    new_id = response.json()["id"]
    print(f"新菜谱ID: {new_id}")
else:
    print(f"\n❌ 创建失败: {response.text}")