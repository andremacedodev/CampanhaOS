"""
Porta (interface) do repositório de FinanceTransaction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.finance.entities import FinanceTransaction


@dataclass(frozen=True)
class FinanceFilter:
    type: str | None = None
    category: str | None = None
    occurred_after: date | None = None
    occurred_before: date | None = None
    # Um de "pago"/"parcial"/"pendente"/"atrasado" — mesmo que
    # `payment_status` não seja mais armazenado, dá pra FILTRAR por ele
    # comparando a soma de pagamentos na consulta (ver implementação em
    # SqlAlchemyFinanceRepository._build_conditions). Só se aplica a
    # despesa — aplicar esse filtro já implica type="despesa" também.
    payment_status: str | None = None
    include_deleted: bool = False


@dataclass(frozen=True)
class FinanceTransactionListItem:
    """
    (lançamento, quantidade de anexos, total já pago) — usado só na
    LISTAGEM, pra mostrar na tela sem precisar abrir cada lançamento
    individualmente. `find_by_id` continua retornando só
    `FinanceTransaction` puro; essas informações extras são uma
    preocupação específica de exibição em lista.
    """

    transaction: FinanceTransaction
    attachment_count: int
    amount_paid: Decimal


@dataclass(frozen=True)
class FinancePage:
    items: list[FinanceTransactionListItem]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


@dataclass(frozen=True)
class FinanceSummary:
    total_receitas: Decimal
    total_despesas: Decimal
    total_doacoes: Decimal
    # Soma real de FinancePayment — só existe pra despesa (receita/doação
    # não têm controle de recebimento parcial, ver ADR do módulo).
    total_pago: Decimal

    @property
    def total_a_pagar(self) -> Decimal:
        """
        O que ainda falta pagar das despesas lançadas — pode ficar
        negativo se pagou mais do que lançou no total (permitido de
        propósito, ver FinanceTransaction.compute_effective_status).
        """
        return self.total_despesas - self.total_pago

    @property
    def saldo_atual(self) -> Decimal:
        """
        Saldo de CAIXA real — usa o que foi de fato PAGO (não o que foi
        só lançado) nas despesas. Receita/doação continuam contando pelo
        valor lançado (sem controle de recebimento parcial nessa versão).
        Esse é o número que reflete "quanto realmente tem", diferente do
        saldo antigo que usava despesas lançadas mesmo sem ainda ter sido
        pagas de verdade.
        """
        return self.total_receitas + self.total_doacoes - self.total_pago


class FinanceRepository(ABC):
    @abstractmethod
    async def save(self, transaction: FinanceTransaction) -> None:
        """Persiste um lançamento novo ou atualiza um existente (upsert por id)."""

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID, transaction_id: UUID) -> FinanceTransaction | None:
        """Busca por id, escopado ao tenant."""

    @abstractmethod
    async def list_paginated(
        self,
        tenant_id: UUID,
        filters: FinanceFilter,
        page: int,
        page_size: int,
    ) -> FinancePage:
        """Lista paginada, mais recentes primeiro (por `occurred_at`)."""

    @abstractmethod
    async def get_summary(self, tenant_id: UUID, filters: FinanceFilter) -> FinanceSummary:
        """
        Totais agregados (soma por tipo) respeitando os MESMOS filtros da
        listagem — calculado via agregação no banco (SUM/GROUP BY), não
        somando em Python, para não precisar carregar todos os registros
        na memória só para totalizar.
        """
