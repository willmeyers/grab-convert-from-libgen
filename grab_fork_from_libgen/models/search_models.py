from enum import Enum

from pydantic import BaseModel, Field

# This ensures that md5 is a valid 32 hexadecimal string.
md5_reg = "^[0-9a-fA-F]{32}$"


class ValidTopics(str, Enum):
    fiction = "fiction"
    sci_tech = "sci-tech"


class SearchEntry(BaseModel):
    # Defines how a valid book entry should look like.
    authors: str = Field(..., alias="author(s)")
    series: str
    title: str
    topic: ValidTopics
    md5: str = Field(..., regex=md5_reg)
    language: str
    extension: str
    size: str

    class Config:
        allow_population_by_field_name = True
