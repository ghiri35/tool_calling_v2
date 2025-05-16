from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from faker import Faker
from datetime import datetime, timedelta
import random

from .models import Order, User
from .db import get_db 

fake = Faker()

def seed_orders(count: int = 10, db: Session = Depends(get_db)):
    db_gen = get_db()
    db = next(db_gen)
    user = User(
        username="ghiri",
        email="ghiripdkt2017@gmail.com",
        hashed_password="ghiri",
        tier="gold",
        has_escalated=False,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    for i in range(10):
        user = User(
                username=fake.user_name(),
                email=fake.email(),
                hashed_password=fake.password(),
                tier=random.choice(["standard", "free", "gold", "platinum"]),
                has_escalated=False,
                role=random.choice(["user", "manager", "admin"])
            )
        db.add(user)
        db.commit()
        db.refresh(user)



    for _ in range(count):
        status = "active"
        choice = random.random()
        if choice <= 0.35:
            status = "dispatched"
        elif choice > 0.85:
            status = "completed"
        elif 0.7 < choice <= 0.85:
            status = "cancelled" 
        created_at = fake.date_time_between(start_date="-5d", end_date="now")

        order = Order(
            user_id=random.randint(1, 10),
            product_name=fake.word(),
            status=status,
            created_at=created_at,
            product_type=random.choice(["limited edition", "special item"]),
            dispatched_at=created_at + timedelta(days=random.randint(0, 2)) if choice <= 0.35 else None,
            completed_at=created_at + timedelta(days=random.randint(1, 3)) if choice > 0.85 else None,
            cancelled_at=created_at + timedelta(hours=1) if 0.7 < choice <= 0.85 else None
        )
        db.add(order)
    db.commit()
    return {"message": f"{count} orders seeded successfully."}

        