"""Categories endpoints (публичные, кэшируемые)."""
from fastapi import APIRouter

from app.schemas import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories():
    raise NotImplementedError  # TODO: repair/cleaning/leisure/kids из БД


@router.get("/{slug}", response_model=CategoryOut)
def get_category(slug: str):
    raise NotImplementedError
