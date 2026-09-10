"""
Porta (interface) do repositório de FinancePayment.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.domain.finance.entities import FinancePayment


class FinancePaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment: FinancePayment) -> None: ...

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID, payment_id: UUID) -> FinancePayment | None: ...

    @abstractmethod
    async def list_by_transaction(self, tenant_id: UUID, transaction_id: UUID) -> list[FinancePayment]: ...

    @abstractmethod
    async def get_total_paid(self, tenant_id: UUID, transaction_id: UUID) -> Decimal:
        """Soma de todos os pagamentos já registrados pra essa despesa — base do status calculado."""

    @abstractmethod
    async def delete(self, tenant_id: UUID, payment_id: UUID) -> None: ...
