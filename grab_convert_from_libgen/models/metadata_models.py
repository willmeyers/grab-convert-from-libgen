from enum import Enum
from pydantic import BaseModel, Field, validator
from ..exceptions import MetadataError


class MetadataResponse(BaseModel):
    download_links: dict | None
    description: str | None
    title: str | None
    authors: str | None

    @validator("download_links")
    def validate_dlinks(cls, v):
        if v is None:
            raise MetadataError("Couldn't get download links for this md5.")
        return v
