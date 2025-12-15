# main.py - 完整版（一字不差）
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from typing import List, Optional
from recipe_service import recommend_recipes
from models import SessionLocal, Recipe, User
from auth import verify_password, get_password_hash, create_access_token
import json

app = FastAPI()

_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
_origins = [o.strip() for o in _origins_raw.split(",") if o.strip()]
_allow_credentials = _origins != ["*"]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_credentials=_allow_credentials, allow_methods=["*"], allow_headers=["*"])

class RecipeRequest(BaseModel):
    ingredients: List[str]
    tags: Optional[List[str]] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/recommend")
def recommend(request: RecipeRequest):
    recipes = recommend_recipes(request.ingredients, request.tags)
    return {
        "user_ingredients": request.ingredients,
        "filter_tags": request.tags,
        "recommendations": recipes,
        "total": len(recipes)
    }

@app.on_event("startup")
def seed_data():
    from models import SessionLocal, Recipe
    import json
    db = SessionLocal()
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "recipes.json")
        if not os.path.exists(data_path):
            return
        with open(data_path, "r", encoding="utf-8") as f:
            recipes_data = json.load(f)
        for r in recipes_data:
            exists = db.query(Recipe).filter(Recipe.id == r["id"]).first()
            if exists:
                continue
            db.add(Recipe(
                id=r["id"],
                name=r["name"],
                ingredients=json.dumps(r["ingredients"], ensure_ascii=False),
                steps=json.dumps(r["steps"], ensure_ascii=False),
                time=r["time"],
                tags=json.dumps(r["tags"], ensure_ascii=False)
            ))
        db.commit()
    finally:
        db.close()

# main.py - 只替换这两个函数

@app.post("/register")
def register(user: UserCreate):
    """用户注册（修复密码长度限制）"""
    db = SessionLocal()
    try:
        # 检查用户是否存在
        existing = db.query(User).filter(User.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 修复：截断密码到72字节，避免bcrypt崩溃
        password_to_hash = user.password[:72]

        # 创建新用户
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(password_to_hash)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"message": "注册成功", "user_id": db_user.id}
    except ValueError as e:
        # 捕获bcrypt密码长度错误
        if "password cannot be longer than 72 bytes" in str(e):
            raise HTTPException(status_code=400, detail="密码不能超过72字节")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
    finally:
        db.close()


@app.post("/login")
def login(user: UserLogin):
    """用户登录（修复版）"""
    db = SessionLocal()
    try:
        print(f"登录尝试: 用户名={user.username}")  # 调试日志

        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            print("用户不存在")
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        print(f"找到用户: {db_user.username}, 哈希: {db_user.hashed_password[:20]}...")

        # 验证密码
        if not verify_password(user.password, db_user.hashed_password):
            print("密码验证失败")
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 生成令牌
        access_token = create_access_token(data={"sub": db_user.username})
        print(f"令牌生成成功: {access_token[:30]}...")

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "AI食谱API服务正常"}
