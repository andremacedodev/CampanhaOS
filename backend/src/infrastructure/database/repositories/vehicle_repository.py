"""
Implementação concreta de VehicleRepository usando SQLAlchemy async.
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.vehicles.entities import StickeredVehicle
from src.domain.vehicles.repository import VehicleFilter, VehiclePage, VehicleRepository
from src.infrastructure.database.models import StickeredVehicleModel


class SqlAlchemyVehicleRepository(VehicleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, vehicle: StickeredVehicle) -> None:
        existing = await self._session.get(StickeredVehicleModel, vehicle.id)
        if existing is None:
            model = StickeredVehicleModel(
                id=vehicle.id,
                tenant_id=vehicle.tenant_id,
                created_by_user_id=vehicle.created_by_user_id,
                plate=vehicle.plate,
                owner_name=vehicle.owner_name,
                voter_id=vehicle.voter_id,
                model=vehicle.model,
                city=vehicle.city,
                stickered_at=vehicle.stickered_at,
                deleted_at=vehicle.deleted_at,
                photo_storage_key=vehicle.photo_storage_key,
                photo_filename=vehicle.photo_filename,
                photo_content_type=vehicle.photo_content_type,
                photo_size_bytes=vehicle.photo_size_bytes,
            )
            self._session.add(model)
        else:
            existing.plate = vehicle.plate
            existing.owner_name = vehicle.owner_name
            existing.voter_id = vehicle.voter_id
            existing.model = vehicle.model
            existing.city = vehicle.city
            existing.stickered_at = vehicle.stickered_at
            existing.deleted_at = vehicle.deleted_at
            existing.photo_storage_key = vehicle.photo_storage_key
            existing.photo_filename = vehicle.photo_filename
            existing.photo_content_type = vehicle.photo_content_type
            existing.photo_size_bytes = vehicle.photo_size_bytes

        await self._session.flush()

    async def find_by_id(self, tenant_id: UUID, vehicle_id: UUID) -> StickeredVehicle | None:
        stmt = select(StickeredVehicleModel).where(
            StickeredVehicleModel.tenant_id == tenant_id, StickeredVehicleModel.id == vehicle_id
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_paginated(
        self, tenant_id: UUID, filters: VehicleFilter, page: int, page_size: int
    ) -> VehiclePage:
        conditions = [StickeredVehicleModel.tenant_id == tenant_id, StickeredVehicleModel.deleted_at.is_(None)]
        if filters.search_text:
            like_pattern = f"%{filters.search_text}%"
            conditions.append(
                or_(
                    StickeredVehicleModel.plate.ilike(like_pattern),
                    StickeredVehicleModel.owner_name.ilike(like_pattern),
                    StickeredVehicleModel.model.ilike(like_pattern),
                )
            )

        count_stmt = select(func.count()).select_from(StickeredVehicleModel).where(*conditions)
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(StickeredVehicleModel)
            .where(*conditions)
            .order_by(StickeredVehicleModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        models = (await self._session.execute(stmt)).scalars().all()

        return VehiclePage(
            items=[self._to_domain(m) for m in models], total=total, page=page, page_size=page_size
        )

    async def count_total(self, tenant_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(StickeredVehicleModel)
            .where(StickeredVehicleModel.tenant_id == tenant_id, StickeredVehicleModel.deleted_at.is_(None))
        )
        return (await self._session.execute(stmt)).scalar_one()

    def _to_domain(self, model: StickeredVehicleModel) -> StickeredVehicle:
        return StickeredVehicle(
            id=model.id,
            tenant_id=model.tenant_id,
            created_by_user_id=model.created_by_user_id,
            plate=model.plate,
            owner_name=model.owner_name,
            voter_id=model.voter_id,
            model=model.model,
            city=model.city,
            stickered_at=model.stickered_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            photo_storage_key=model.photo_storage_key,
            photo_filename=model.photo_filename,
            photo_content_type=model.photo_content_type,
            photo_size_bytes=model.photo_size_bytes,
        )
