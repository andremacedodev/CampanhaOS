from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateFinanceTransactionInput:
    tenant_id: UUID
    created_by_user_id: UUID
    type: str
    category: str
    amount: Decimal
    occurred_at: date
    description: str | None = None


@dataclass(frozen=True)
class UpdateFinanceTransactionInput:
    tenant_id: UUID
    transaction_id: UUID
    type: str | None = None
    category: str | None = None
    amount: Decimal | None = None
    description: str | None = None
    occurred_at: date | None = None


@dataclass(frozen=True)
class GetFinanceTransactionInput:
    tenant_id: UUID
    transaction_id: UUID


@dataclass(frozen=True)
class DeleteFinanceTransactionInput:
    tenant_id: UUID
    transaction_id: UUID


@dataclass(frozen=True)
class ListFinanceTransactionsInput:
    tenant_id: UUID
    type: str | None = None
    category: str | None = None
    search_text: str | None = None
    occurred_after: date | None = None
    occurred_before: date | None = None
    payment_status: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class FinanceTransactionOutput:
    id: UUID
    created_by_user_id: UUID
    type: str
    category: str
    amount: Decimal
    description: str | None
    occurred_at: date
    created_at: datetime
    updated_at: datetime
    # None pra receita/doação (não têm controle de pagamento) — só
    # despesa tem um dos 4 valores (pendente/atrasado/parcial/pago),
    # sempre CALCULADO a partir da soma de pagamentos reais, nunca
    # armazenado (ver FinanceTransaction.compute_effective_status).
    effective_payment_status: str | None
    amount_paid: Decimal
    # Pode ficar NEGATIVO se pagou a mais que o lançado — permitido de
    # propósito, sem bloqueio (decisão explícita do usuário).
    amount_remaining: Decimal
    attachment_count: int


@dataclass(frozen=True)
class FinanceSummaryOutput:
    total_receitas: Decimal
    total_despesas: Decimal
    total_doacoes: Decimal
    total_pago: Decimal
    total_a_pagar: Decimal
    saldo_atual: Decimal


@dataclass(frozen=True)
class ListFinanceTransactionsOutput:
    items: list[FinanceTransactionOutput]
    total: int
    page: int
    page_size: int
    total_pages: int
    summary: FinanceSummaryOutput


@dataclass(frozen=True)
class AddFinanceAttachmentInput:
    tenant_id: UUID
    transaction_id: UUID
    uploaded_by_user_id: UUID
    category: str
    filename: str
    file_bytes: bytes


@dataclass(frozen=True)
class RemoveFinanceAttachmentInput:
    tenant_id: UUID
    transaction_id: UUID
    attachment_id: UUID


@dataclass(frozen=True)
class ListFinanceAttachmentsInput:
    tenant_id: UUID
    transaction_id: UUID


@dataclass(frozen=True)
class FinanceAttachmentOutput:
    id: UUID
    transaction_id: UUID
    category: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


@dataclass(frozen=True)
class GetFinanceAttachmentDownloadUrlInput:
    tenant_id: UUID
    transaction_id: UUID
    attachment_id: UUID


@dataclass(frozen=True)
class GetFinanceAttachmentDownloadUrlOutput:
    download_url: str
    filename: str


@dataclass(frozen=True)
class AddFinancePaymentInput:
    tenant_id: UUID
    transaction_id: UUID
    created_by_user_id: UUID
    amount: Decimal
    paid_at: date


@dataclass(frozen=True)
class RemoveFinancePaymentInput:
    tenant_id: UUID
    transaction_id: UUID
    payment_id: UUID


@dataclass(frozen=True)
class ListFinancePaymentsInput:
    tenant_id: UUID
    transaction_id: UUID


@dataclass(frozen=True)
class FinancePaymentOutput:
    id: UUID
    transaction_id: UUID
    amount: Decimal
    paid_at: date
    created_at: datetime
