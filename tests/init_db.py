from models import SessionLocal, Recipe
import json

# 把recipes.json导入数据库
with open("../data/recipes.json", "r", encoding="utf-8") as f:
    recipes_data = json.load(f)

db = SessionLocal()
for recipe in recipes_data:
    db.add(Recipe(
        id=recipe["id"],
        name=recipe["name"],
        ingredients=json.dumps(recipe["ingredients"], ensure_ascii=False),
        steps=json.dumps(recipe["steps"], ensure_ascii=False),
        time=recipe["time"],
        tags=json.dumps(recipe["tags"], ensure_ascii=False)
    ))
db.commit()
db.close()
print("✅ 数据库初始化完成")