"""
Run this once to create your first admin login.
Usage: python create_admin.py
"""
from app.database import SessionLocal, Base, engine
from app.models import Admin
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

email = input("Admin email: ").strip()
password = input("Admin password: ").strip()

existing = db.query(Admin).filter(Admin.email == email).first()
if existing:
    print("An admin with this email already exists.")
else:
    admin = Admin(email=email, password_hash=hash_password(password))
    db.add(admin)
    db.commit()
    print(f"Admin account created for {email}")

db.close()
