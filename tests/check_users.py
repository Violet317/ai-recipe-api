from models import SessionLocal, User

db = SessionLocal()
users = db.query(User).all()
print(f"用户表里有 {len(users)} 个用户")
db.close()