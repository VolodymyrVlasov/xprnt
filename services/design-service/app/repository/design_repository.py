import uuid
from typing import Optional

from sqlalchemy import select, update
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
        guest_session_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> CustomerDesigns:
        obj = CustomerDesigns(
            filename=filename,
            path=path,
            previewPath=preview_path,
            design_metadata=metadata,
            guest_session_id=guest_session_id,
            user_id=user_id,
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

    async def update_customer_design(
        self,
        db: AsyncSession,
        obj: CustomerDesigns,
        updates: dict,
    ) -> CustomerDesigns:
        for key, value in updates.items():
            setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

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

    async def claim_by_session(
        self,
        db: AsyncSession,
        guest_session_id: str,
        user_id: uuid.UUID,
    ) -> int:
        """Set user_id on all unclaimed designs for a guest session. Returns row count."""
        result = await db.execute(
            update(CustomerDesigns)
            .where(
                CustomerDesigns.guest_session_id == guest_session_id,
                CustomerDesigns.user_id.is_(None),
            )
            .values(user_id=user_id)
        )
        await db.commit()
        return result.rowcount


design_repo = DesignRepository()
