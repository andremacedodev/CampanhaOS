"""
Implementação concreta de FinancePaymentRepository usando SQLAlchemy async.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.finance.entities import FinancePayment
from src.domain.finance.payment_repository import FinancePaymentRepository
from src.infrastructure.database.models import FinancePaymentModel


class SqlAlchemyFinancePaymentRepository(FinancePaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, payment: FinancePayment) -> None:
        model = FinancePaymentModel(
            id=payment.id,
            tenant_id=payment.tenant_id,
            transaction_id=payment.transaction_id,
            created_by_user_id=payment.created_by_user_id,
            amount=payment.amount,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_id(self, tenant_id: UUID, payment_id: UUID) -> FinancePayment | None:
        stmt = select(FinancePaymentModel).where(
            FinancePaymentModel.tenant_id == tenant_id, FinancePaymentModel.id == payment_id
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> list[FinancePayment]:
        stmt = (
            select(FinancePaymentModel)
            .where(FinancePaymentModel.tenant_id == tenant_id, FinancePaymentModel.transaction_id == transaction_id)
            .order_by(FinancePaymentModel.paid_at.desc(), FinancePaymentModel.created_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_total_paid(self, tenant_id: UUID, transaction_id: UUID) -> Decimal:
        stmt = (
            select(func.coalesce(func.sum(FinancePaymentModel.amount), 0))
            .where(FinancePaymentModel.tenant_id == tenant_id, FinancePaymentModel.transaction_id == transaction_id)
        )
        return (await self._session.execute(stmt)).scalar_one()

    async def delete(self, tenant_id: UUID, payment_id: UUID) -> None:
        model = await self._session.get(FinancePaymentModel, payment_id)
        if model is not None and model.tenant_id == tenant_id:
            await self._session.delete(model)
            await self._session.flush()

    def _to_domain(self, model: FinancePaymentModel) -> FinancePayment:
        return FinancePayment(
            id=model.id,
            tenant_id=model.tenant_id,
            transaction_id=model.transaction_id,
            created_by_user_id=model.created_by_user_id,
            amount=model.amount,
            paid_at=model.paid_at,
            created_at=model.created_at,
        )
