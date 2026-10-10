from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(
    prefix="/api/contacts",
    tags=["contacts"],
)


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    return crud.create_contact(
        db,
        current_user.id,
        contact_data,
    )


@router.get(
    "/search",
    response_model=list[ContactResponse],
)
def search_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    return crud.search_contacts(
        db,
        current_user.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )


@router.get(
    "/upcoming-birthdays",
    response_model=list[ContactResponse],
)
def upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    return crud.get_upcoming_birthdays(
        db,
        current_user.id,
        days=7,
    )


@router.get(
    "",
    response_model=list[ContactResponse],
)
def get_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    return crud.get_contacts(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = crud.get_contact(
        db,
        current_user.id,
        contact_id,
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
)
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = crud.get_contact(
        db,
        current_user.id,
        contact_id,
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    return crud.update_contact(
        db,
        contact,
        contact_data,
    )


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    contact = crud.get_contact(
        db,
        current_user.id,
        contact_id,
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )

    crud.delete_contact(db, contact)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
