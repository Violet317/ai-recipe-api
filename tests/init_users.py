# init_users.py - 初始化用户表
from models import engine, Base

# 执行创建表（如果表已存在则跳过）
Base.metadata.create_all(engine)
print("✅ 用户表创建成功！")