"""
Implementação concreta de FinancePaymentRepository usando SQLAlchemy async.
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.finance.entities import FinancePayment
from src.domain.finance.payment_repository import FinancePaymentRepository, PaymentWithTransactionInfo
from src.infrastructure.database.models import FinancePaymentModel, FinanceTransactionModel


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

    async def list_in_range_with_transaction_info(
        self, tenant_id: UUID, paid_after: date | None, paid_before: date | None
    ) -> list[PaymentWithTransactionInfo]:
        # IMPORTANTE: filtra também pela despesa NÃO estar excluída —
        # exclusão é "suave" (só marca `deleted_at`, não apaga os
        # pagamentos que já existiam), então sem essa checagem os
        # pagamentos de uma despesa excluída continuariam aparecendo no
        # extrato pra sempre (bug real encontrado em produção).
        conditions = [
            FinancePaymentModel.tenant_id == tenant_id,
            FinanceTransactionModel.deleted_at.is_(None),
        ]
        if paid_after:
            conditions.append(FinancePaymentModel.paid_at >= paid_after)
        if paid_before:
            conditions.append(FinancePaymentModel.paid_at <= paid_before)

        stmt = (
            select(FinancePaymentModel, FinanceTransactionModel.category, FinanceTransactionModel.description)
            .join(FinanceTransactionModel, FinancePaymentModel.transaction_id == FinanceTransactionModel.id)
            .where(*conditions)
            .order_by(FinancePaymentModel.paid_at)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            PaymentWithTransactionInfo(payment=self._to_domain(payment_model), category=category, description=description)
            for payment_model, category, description in rows
        ]

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