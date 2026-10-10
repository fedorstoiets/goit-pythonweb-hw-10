from datetime import date, timedelta
import random

from faker import Faker
from sqlalchemy import delete

from app.database import SessionLocal
from app.models import Contact, User
from app.security import hash_password

fake = Faker()


def safe_birthday(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 28)


def seed_database() -> None:
    today = date.today()

    with SessionLocal() as db:
        db.execute(delete(Contact))
        db.execute(delete(User))
        db.commit()

        user = User(
            username="demo",
            email="demo@example.com",
            password_hash=hash_password("DemoPassword123!"),
            is_verified=True,
        )
        db.add(user)
        db.flush()

        contacts: list[Contact] = []

        for index in range(10):
            birthday = fake.date_of_birth(
                minimum_age=18,
                maximum_age=70,
            )

            if index == 0:
                upcoming = today + timedelta(days=3)
                birthday = safe_birthday(
                    random.randint(1970, 2004),
                    upcoming.month,
                    upcoming.day,
                )

            contacts.append(
                Contact(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=f"contact{index + 1}@example.com",
                    phone=f"+1 617 555 {1000 + index}",
                    birthday=birthday,
                    additional_data=fake.sentence(),
                    owner_id=user.id,
                )
            )

        db.add_all(contacts)
        db.commit()

        print("Seed complete.")
        print("Demo user: demo@example.com")
        print("Demo password: DemoPassword123!")
        print(f"Contacts: {len(contacts)}")


if __name__ == "__main__":
    seed_database()
