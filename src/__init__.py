"""Wedaita BiomCP package."""

from enum import Enum
from typing import Any, TypeVar, Union
from pydantic import BaseModel

T = TypeVar("T")


class StrEnum(str, Enum):
    """String enum class."""

    def __str__(self) -> str:
        return self.value


def ensure_list(value: Union[T, list[T], None]) -> list[T]:
    """Ensure the value is a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value] 


class ToolError(Exception):
    """Base class for all tool errors"""


class WedaitaBaseModel(BaseModel):
    """Base class for all data models"""