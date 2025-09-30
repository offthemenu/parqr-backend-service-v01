from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user_count = db.query(User).count()
print(f"Total Users: {user_count}")
db.close()
