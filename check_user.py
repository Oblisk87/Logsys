
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User, Base, pwd_context

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def check_user():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "Freedom").first()
    if user:
        print(f"User found: {user.username}")
        print(f"Password hash: {user.password}")
        print(f"Password verification: {pwd_context.verify('Jayden', user.password)}")
    else:
        print("User not found")
    db.close()

if __name__ == "__main__":
    check_user()
