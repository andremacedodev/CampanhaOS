"""
Implementação concreta de FinanceAttachmentRepository usando SQLAlchemy async.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.finance.attachment_repository import FinanceAttachmentRepository
from src.domain.finance.entities import FinanceAttachment
from src.infrastructure.database.models import FinanceAttachmentModel


class SqlAlchemyFinanceAttachmentRepository(FinanceAttachmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, attachment: FinanceAttachment) -> None:
        model = FinanceAttachmentModel(
            id=attachment.id,
            tenant_id=attachment.tenant_id,
            transaction_id=attachment.transaction_id,
            uploaded_by_user_id=attachment.uploaded_by_user_id,
            category=attachment.category,
            storage_key=attachment.storage_key,
            filename=attachment.filename,
            content_type=attachment.content_type,
            size_bytes=attachment.size_bytes,
            uploaded_at=attachment.uploaded_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, tenant_id: UUID, attachment_id: UUID) -> FinanceAttachment | None:
        stmt = select(FinanceAttachmentModel).where(
            FinanceAttachmentModel.tenant_id == tenant_id, FinanceAttachmentModel.id == attachment_id
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> list[FinanceAttachment]:
        stmt = (
            select(FinanceAttachmentModel)
            .where(
                FinanceAttachmentModel.tenant_id == tenant_id,
                FinanceAttachmentModel.transaction_id == transaction_id,
            )
            .order_by(FinanceAttachmentModel.uploaded_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [self._to_domain(m) for m in models]

    async def count_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(FinanceAttachmentModel)
            .where(
                FinanceAttachmentModel.tenant_id == tenant_id,
                FinanceAttachmentModel.transaction_id == transaction_id,
            )
        )
        return (await self._session.execute(stmt)).scalar_one()

    async def delete(self, tenant_id: UUID, attachment_id: UUID) -> None:
        model = await self._session.get(FinanceAttachmentModel, attachment_id)
        if model is not None and model.tenant_id == tenant_id:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: FinanceAttachmentModel) -> FinanceAttachment:
        return FinanceAttachment(
            id=model.id,
            tenant_id=model.tenant_id,
            transaction_id=model.transaction_id,
            uploaded_by_user_id=model.uploaded_by_user_id,
            category=model.category,
            storage_key=model.storage_key,
            filename=model.filename,
            content_type=model.content_type,
            size_bytes=model.size_bytes,
            uploaded_at=model.uploaded_at,
        )
