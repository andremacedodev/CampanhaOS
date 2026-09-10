"""
Schemas Pydantic dos endpoints financeiros (Financeiro básico + anexos múltiplos).
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TransactionType = Literal["receita", "despesa", "doacao"]
AttachmentCategory = Literal["comprovante", "contrato", "orcamento", "outro"]


class FinanceTransactionCreateRequest(BaseModel):
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, description="Sempre positivo — o tipo determina se soma ou subtrai")
    occurred_at: date
    description: str | None = None


class FinanceTransactionUpdateRequest(BaseModel):
    type: TransactionType | None = None
    category: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0)
    occurred_at: date | None = None
    description: str | None = None


class FinanceTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by_user_id: UUID
    type: str
    category: str
    amount: Decimal
    description: str | None
    occurred_at: date
    created_at: datetime
    updated_at: datetime
    # None pra receita/doação — só despesa tem controle de pagamento
    # nessa versão. Nunca escolhido manualmente, sempre calculado a
    # partir da soma de pagamentos reais registrados.
    effective_payment_status: str | None
    amount_paid: Decimal
    amount_remaining: Decimal
    attachment_count: int


class FinanceSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_receitas: Decimal
    total_despesas: Decimal
    total_doacoes: Decimal
    total_pago: Decimal
    total_a_pagar: Decimal
    saldo_atual: Decimal


class FinanceTransactionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[FinanceTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    summary: FinanceSummaryResponse


class FinanceAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: UUID
    category: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class FinanceAttachmentListResponse(BaseModel):
    items: list[FinanceAttachmentResponse]


class FinanceAttachmentDownloadResponse(BaseModel):
    download_url: str
    filename: str


class FinancePaymentCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    paid_at: date


class FinancePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: UUID
    amount: Decimal
    paid_at: date
    created_at: datetime


class FinancePaymentListResponse(BaseModel):
    items: list[FinancePaymentResponse]
