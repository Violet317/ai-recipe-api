import requests

# 测试根路径
response = requests.get("http://localhost:8000/")
print("根路径状态码:", response.status_code)
print("根路径内容:", response.text)

# 测试推荐接口
response = requests.post(
    "http://localhost:8000/recommend",
    json={"ingredients": ["番茄", "鸡蛋"]}
)
print("推荐接口状态码:", response.status_code)
print("推荐接口内容:", response.text)