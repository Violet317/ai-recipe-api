# recipe_service.py - 数据库版本
import json
from typing import List, Dict, Optional
from models import SessionLocal, Recipe


def recommend_recipes(user_ingredients: List[str], filter_tags: Optional[List[str]] = None) -> List[Dict]:
    """从数据库查询并推荐菜谱"""
    db = SessionLocal()
    try:
        # 从数据库查询所有菜谱
        recipes_db = db.query(Recipe).all()

        # 转换格式
        db_recipes = []
        for r in recipes_db:
            db_recipes.append({
                "id": r.id,
                "name": r.name,
                "ingredients": json.loads(r.ingredients),
                "steps": json.loads(r.steps),
                "time": r.time,
                "tags": json.loads(r.tags)
            })

        # 食材匹配逻辑（不变）
        user_ingredients = [ing.strip() for ing in user_ingredients]
        filter_tags = filter_tags or []

        recommendations = []
        for recipe in db_recipes:
            # 标签过滤
            if filter_tags and not any(tag in recipe["tags"] for tag in filter_tags):
                continue

            # 食材匹配
            matched = set(user_ingredients) & set(recipe["ingredients"])
            if len(matched) >= 2:
                recommendations.append({
                    "id": recipe["id"],
                    "name": recipe["name"],
                    "match_rate": round(len(matched) / len(recipe["ingredients"]), 2),
                    "missing_ingredients": list(set(recipe["ingredients"]) - matched),
                    "time": recipe["time"],
                    "tags": recipe["tags"]
                })

        return sorted(recommendations, key=lambda x: x["match_rate"], reverse=True)
    finally:
        db.close()


# 测试函数
if __name__ == "__main__":
    result = recommend_recipes(["番茄", "鸡蛋"])
    print(f"推荐结果: {len(result)} 个菜谱")
    for r in result:
        print(f"- {r['name']} (匹配度: {r['match_rate']})")