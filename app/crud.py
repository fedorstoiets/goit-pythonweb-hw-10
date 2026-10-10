from datetime import date, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Contact, User
from app.schemas import ContactCreate, ContactUpdate, UserCreate
from app.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=str(user_data.email),
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_contact(
    db: Session,
    owner_id: int,
    contact_data: ContactCreate,
) -> Contact:
    contact = Contact(
        **contact_data.model_dump(),
        owner_id=owner_id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contacts(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Contact]:
    statement = (
        select(Contact)
        .where(Contact.owner_id == owner_id)
        .order_by(Contact.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_contact(
    db: Session,
    owner_id: int,
    contact_id: int,
) -> Contact | None:
    statement = select(Contact).where(
        Contact.id == contact_id,
        Contact.owner_id == owner_id,
    )
    return db.scalar(statement)


def update_contact(
    db: Session,
    contact: Contact,
    contact_data: ContactUpdate,
) -> Contact:
    updates = contact_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: Contact) -> None:
    db.delete(contact)
    db.commit()


def search_contacts(
    db: Session,
    owner_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> list[Contact]:
    filters = []

    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    statement = select(Contact).where(Contact.owner_id == owner_id)

    if filters:
        statement = statement.where(or_(*filters))

    return list(db.scalars(statement.order_by(Contact.id)).all())


def get_upcoming_birthdays(
    db: Session,
    owner_id: int,
    days: int = 7,
) -> list[Contact]:
    today = date.today()
    end_date = today + timedelta(days=days)

    contacts = list(
        db.scalars(select(Contact).where(Contact.owner_id == owner_id)).all()
    )

    upcoming: list[tuple[int, Contact]] = []

    for contact in contacts:
        birthday = contact.birthday

        try:
            next_birthday = birthday.replace(year=today.year)
        except ValueError:
            next_birthday = date(today.year, 2, 28)

        if next_birthday < today:
            try:
                next_birthday = birthday.replace(year=today.year + 1)
            except ValueError:
                next_birthday = date(today.year + 1, 2, 28)

        if today <= next_birthday <= end_date:
            upcoming.append(((next_birthday - today).days, contact))

    upcoming.sort(key=lambda item: item[0])
    return [contact for _, contact in upcoming]
