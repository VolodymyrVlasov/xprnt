from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Map design_metadata ORM attr → metadata schema field
        if hasattr(obj, "design_metadata"):
            data = {
                "id": obj.id,
                "path": obj.path,
                "filename": obj.filename,
                "previewPath": obj.previewPath,
                "metadata": obj.design_metadata,
            }
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)


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
