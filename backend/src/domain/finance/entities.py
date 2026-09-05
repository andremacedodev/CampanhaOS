"""
Entidades de domínio do módulo financeiro: FinanceTransaction (lançamento
financeiro) e FinanceAttachment (documento anexado a um lançamento).

RF-12 (Fase 1): receitas, despesas e doações da campanha.

Decisão crítica: `amount` é `Decimal`, nunca `float` — dinheiro não pode
usar ponto flutuante binário, que não representa a maioria dos valores
decimais com exatidão (ex: 0.1 + 0.2 != 0.3 em float). Em milhares de
lançamentos, esse erro se acumula e gera divergência de caixa real.

`amount` é sempre armazenado POSITIVO — é o campo `type` que determina se
o valor soma ou subtrai num relatório (RN implícita: receita e doação
somam, despesa subtrai). Isso evita a ambiguidade de "valor negativo
representando uma despesa", que é fácil de inverter por engano em algum
cálculo futuro.

FinanceAttachment é uma entidade PRÓPRIA (não campos soltos dentro de
FinanceTransaction) — um lançamento pode ter vários documentos
(comprovante, contrato, orçamento), até um limite de 10. Cada anexo tem
seu próprio ciclo de vida (upload/remoção independente).
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.shared.exceptions import DomainError, InvalidNameError

_VALID_TRANSACTION_TYPES = frozenset({"receita", "despesa", "doacao"})

# Tipos de anexo aceitos — nota fiscal, cupom fiscal, comprovante,
# contrato, orçamento. Só imagem e PDF, nada de tipo executável/script —
# checagem de verdade (conteúdo real do arquivo, não extensão) acontece
# na camada de infraestrutura (ver infrastructure/storage/file_signature.py),
# aqui só validamos que o content_type declarado está na lista permitida.
MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
VALID_ATTACHMENT_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "application/pdf"})

# Categoria é só pra organizar a visualização — não muda nenhuma regra de
# negócio nem validação, é puramente descritivo.
VALID_ATTACHMENT_CATEGORIES = frozenset({"comprovante", "contrato", "orcamento", "outro"})

MAX_ATTACHMENTS_PER_TRANSACTION = 10

# Só 2 estados são ARMAZENADOS — "atrasado" nunca é gravado no banco, é
# sempre CALCULADO na hora de exibir (pendente + data já passada = mostra
# como atrasado). Guardar "atrasado" de verdade exigiria um job rodando
# todo dia só pra atualizar status conforme o tempo passa — desnecessário
# quando dá pra calcular isso a qualquer momento a partir da data.
VALID_PAYMENT_STATUSES = frozenset({"pago", "pendente"})


class InvalidTransactionTypeError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(
            f"Tipo de lançamento '{value}' inválido. Valores aceitos: {', '.join(sorted(_VALID_TRANSACTION_TYPES))}"
        )


class InvalidAmountError(DomainError):
    def __init__(self) -> None:
        super().__init__("O valor do lançamento precisa ser maior que zero")


class InvalidPaymentStatusError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(
            f"Status de pagamento '{value}' inválido. Valores aceitos: {', '.join(sorted(VALID_PAYMENT_STATUSES))}"
        )


class InvalidAttachmentError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidAttachmentCategoryError(DomainError):
    def __init__(self, value: str) -> None:
        super().__init__(
            f"Categoria de anexo '{value}' inválida. Valores aceitos: "
            f"{', '.join(sorted(VALID_ATTACHMENT_CATEGORIES))}"
        )


class TooManyAttachmentsError(DomainError):
    def __init__(self) -> None:
        super().__init__(f"Limite de {MAX_ATTACHMENTS_PER_TRANSACTION} anexos por lançamento atingido")


@dataclass
class FinanceTransaction:
    id: UUID
    tenant_id: UUID
    created_by_user_id: UUID
    type: str
    category: str
    amount: Decimal
    description: str | None
    occurred_at: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    # Default "pago" — lançamentos criados sem informar nada continuam
    # representando o comportamento de antes dessa funcionalidade
    # existir (a maioria já estava paga; quem cadastra escolhe
    # "pendente" só quando for o caso).
    payment_status: str = "pago"

    @staticmethod
    def create(
        tenant_id: UUID,
        created_by_user_id: UUID,
        type: str,
        category: str,
        amount: Decimal,
        occurred_at: date,
        description: str | None = None,
        payment_status: str = "pago",
    ) -> "FinanceTransaction":
        FinanceTransaction._validate_type(type)
        FinanceTransaction._validate_category(category)
        FinanceTransaction._validate_amount(amount)
        FinanceTransaction._validate_payment_status(payment_status)

        now = datetime.now(UTC)
        return FinanceTransaction(
            id=uuid4(),
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id,
            type=type,
            category=category.strip(),
            amount=amount,
            description=description,
            occurred_at=occurred_at,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            payment_status=payment_status,
        )

    @staticmethod
    def _validate_type(type_: str) -> None:
        if type_ not in _VALID_TRANSACTION_TYPES:
            raise InvalidTransactionTypeError(type_)

    @staticmethod
    def _validate_category(category: str) -> None:
        if not category or not category.strip():
            raise InvalidNameError("Categoria do lançamento não pode ser vazia")

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidAmountError

    @staticmethod
    def _validate_payment_status(payment_status: str) -> None:
        if payment_status not in VALID_PAYMENT_STATUSES:
            raise InvalidPaymentStatusError(payment_status)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def signed_amount(self) -> Decimal:
        """
        Valor com sinal aplicado conforme o tipo — usado só para cálculo
        de saldo (nunca persistido; `amount` no banco é sempre positivo).
        """
        return -self.amount if self.type == "despesa" else self.amount

    def effective_payment_status(self, today: date) -> str:
        """
        Status "de exibição" — igual a `payment_status`, exceto quando
        está "pendente" E a data do lançamento já passou, caso em que
        vira "atrasado". Nunca gravado no banco, sempre calculado com a
        data atual passada por quem chama (facilita teste — sem isso,
        um teste escrito hoje quebraria sozinho amanhã).
        """
        if self.payment_status == "pendente" and self.occurred_at < today:
            return "atrasado"
        return self.payment_status

    def update_details(
        self,
        *,
        type: str | None = None,
        category: str | None = None,
        amount: Decimal | None = None,
        description: str | None = None,
        occurred_at: date | None = None,
        payment_status: str | None = None,
    ) -> None:
        if type is not None:
            FinanceTransaction._validate_type(type)
            self.type = type
        if category is not None:
            FinanceTransaction._validate_category(category)
            self.category = category.strip()
        if amount is not None:
            FinanceTransaction._validate_amount(amount)
            self.amount = amount
        if description is not None:
            self.description = description or None
        if occurred_at is not None:
            self.occurred_at = occurred_at
        if payment_status is not None:
            FinanceTransaction._validate_payment_status(payment_status)
            self.payment_status = payment_status

        self.updated_at = datetime.now(UTC)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)


@dataclass
class FinanceAttachment:
    id: UUID
    tenant_id: UUID
    transaction_id: UUID
    uploaded_by_user_id: UUID
    category: str
    storage_key: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime

    @staticmethod
    def create(
        tenant_id: UUID,
        transaction_id: UUID,
        uploaded_by_user_id: UUID,
        category: str,
        storage_key: str,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> "FinanceAttachment":
        """
        Chamado depois que o arquivo já foi enviado com sucesso pro R2 —
        mesma ordem de sempre: sobe o arquivo primeiro, só depois grava a
        referência. `existing_count_for_transaction` é checado ANTES
        disso, na camada de aplicação (ver AddFinanceAttachmentUseCase),
        não aqui — esta entidade não tem acesso ao repositório pra saber
        quantos anexos já existem.
        """
        if category not in VALID_ATTACHMENT_CATEGORIES:
            raise InvalidAttachmentCategoryError(category)
        if content_type not in VALID_ATTACHMENT_CONTENT_TYPES:
            raise InvalidAttachmentError(f"Tipo de arquivo '{content_type}' não permitido. Aceitos: JPEG, PNG, PDF.")
        if size_bytes <= 0:
            raise InvalidAttachmentError("Arquivo vazio")
        if size_bytes > MAX_ATTACHMENT_SIZE_BYTES:
            raise InvalidAttachmentError(
                f"Arquivo muito grande ({size_bytes / 1024 / 1024:.1f}MB) — limite de "
                f"{MAX_ATTACHMENT_SIZE_BYTES / 1024 / 1024:.0f}MB"
            )

        return FinanceAttachment(
            id=uuid4(),
            tenant_id=tenant_id,
            transaction_id=transaction_id,
            uploaded_by_user_id=uploaded_by_user_id,
            category=category,
            storage_key=storage_key,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            uploaded_at=datetime.now(UTC),
        )
