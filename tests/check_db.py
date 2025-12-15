# check_db.py - 数据库验证脚本
from models import SessionLocal, Recipe
import json


def check_database():
    """查询数据库并打印所有菜谱"""
    db = SessionLocal()
    try:
        recipes = db.query(Recipe).all()

        print("=" * 50)
        print(f"数据库状态：共 {len(recipes)} 个菜谱")
        print("=" * 50)

        for recipe in recipes:
            print(f"【ID: {recipe.id}】{recipe.name}")
            print(f"食材：{json.loads(recipe.ingredients)}")
            print(f"步骤：{len(json.loads(recipe.steps))} 步")
            print(f"时间：{recipe.time} 分钟")
            print(f"标签：{json.loads(recipe.tags)}")
            print("-" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    check_database()