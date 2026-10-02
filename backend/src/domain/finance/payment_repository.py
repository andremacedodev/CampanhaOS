"""
Porta (interface) do repositório de FinancePayment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.finance.entities import FinancePayment


@dataclass(frozen=True)
class PaymentWithTransactionInfo:
    """
    Um pagamento junto com categoria/descrição da despesa a que pertence
    — usado no extrato, que precisa mostrar essa informação sem fazer
    uma consulta extra por pagamento (evita N+1).
    """

    payment: FinancePayment
    category: str
    description: str | None


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

    @abstractmethod
    async def list_in_range_with_transaction_info(
        self, tenant_id: UUID, paid_after: date | None, paid_before: date | None
    ) -> list[PaymentWithTransactionInfo]:
        """
        Pagamentos cuja DATA DE PAGAMENTO (não a data do lançamento) cai
        no período — é isso que forma o extrato de despesas: cada
        pagamento é um movimento de dinheiro de verdade, na data real em
        que saiu, não na data em que a despesa foi lançada no sistema.
        """
