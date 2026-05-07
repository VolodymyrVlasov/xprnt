import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.design import CustomerDesigns, DesignType, Designs, FPDDesigns


class DesignRepository:

    async def create_customer_design(
        self,
        db: AsyncSession,
        filename: str,
        path: str,
        preview_path: Optional[str],
        metadata: Optional[dict],
    ) -> CustomerDesigns:
        obj = CustomerDesigns(
            filename=filename,
            path=path,
            previewPath=preview_path,
            design_metadata=metadata,
        )
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def create_design(
        self,
        db: AsyncSession,
        design_type: DesignType,
        customer_design_id: Optional[uuid.UUID],
        fpd_design_id: Optional[uuid.UUID],
    ) -> Designs:
        obj = Designs(
            designType=design_type,
            customerDesignId=customer_design_id,
            fpdDesignId=fpd_design_id,
        )
        db.add(obj)
        await db.commit()
        # Re-fetch with joined loads
        return await self.get_design_by_id(db, obj.id)

    async def get_design_by_id(
        self,
        db: AsyncSession,
        design_id: uuid.UUID,
    ) -> Optional[Designs]:
        result = await db.execute(
            select(Designs)
            .options(
                joinedload(Designs.customerDesign),
                joinedload(Designs.fpdDesign),
            )
            .where(Designs.id == design_id)
        )
        return result.scalar_one_or_none()


design_repo = DesignRepository()
