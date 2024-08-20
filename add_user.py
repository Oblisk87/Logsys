
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User, Base, pwd_context, UserStatus

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def add_user():
    db = SessionLocal()
    hashed_password = pwd_context.hash("Jayden")
    user = User(email="freedom@example.com", username="Freedom", password=hashed_password, status=UserStatus.active)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User added: {user.username}")
    db.close()

if __name__ == "__main__":
    add_user()
