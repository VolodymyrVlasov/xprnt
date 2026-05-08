from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.design import DesignType


class MetadataField(BaseModel):
    value: Any
    isValid: bool


class CurrentMetadata(BaseModel):
    dpi: MetadataField
    width: MetadataField
    height: MetadataField
    color: MetadataField


class TargetMetadata(BaseModel):
    dpi: int = 300
    width: Optional[float] = None
    height: Optional[float] = None
    color: str = "cmyk"


class DesignMetadata(BaseModel):
    current: CurrentMetadata
    target: TargetMetadata


class CustomerDesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    path: str
    filename: str
    previewPath: Optional[str] = None
    metadata: Optional[DesignMetadata] = None

    @model_validator(mode="before")
    @classmethod
    def _map_design_metadata(cls, data):
        # ORM column is `design_metadata` (python name); Pydantic reads `metadata`
        # which resolves to SQLAlchemy's MetaData object — remap it here.
        if hasattr(data, "design_metadata"):
            return {
                "id": data.id,
                "path": data.path,
                "filename": data.filename,
                "previewPath": data.previewPath,
                "metadata": data.design_metadata,
            }
        return data


class DesignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    designType: DesignType
    fileURL: str
    previewURL: Optional[str] = None
    customerDesign: Optional[CustomerDesignResponse] = None


class UploadDesignRequest(BaseModel):
    targetWidth: Optional[float] = None
    targetHeight: Optional[float] = None
    targetColor: str = "cmyk"
    targetDpi: int = 300
