"""cria finance_payments (pagamento parcial), remove payment_status manual

Revision ID: 0024_finance_payments
Revises: 0023_add_payment_status
Create Date: 2026-09-06

Substitui o status manual (pago/pendente) por um controle de PAGAMENTOS
REAIS — cada linha em finance_payments é um pagamento individual contra
uma despesa, permitindo quitação parcial em várias partes. O status
"pago/pendente/parcial/atrasado" agora é sempre CALCULADO a partir da
soma desses pagamentos, nunca armazenado.

Migração de dados: toda despesa que já estava marcada como "pago" vira
um FinancePayment de valor igual ao lançamento inteiro (data = data do
lançamento) — preserva o estado "já pago" sem perder informação. Despesa
"pendente" simplesmente não ganha nenhum pagamento (soma continua 0,
efetivamente mostrando "pendente"/"atrasado" pelo cálculo novo). Receita
e doação nunca tiveram controle de pagamento de verdade nessa versão —
o status delas é descartado sem substituição (não existe mais pra esses
tipos).
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024_finance_payments"
down_revision: str | None = "0023_add_payment_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("finance_transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_at", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_finance_payments_tenant_id", "finance_payments", ["tenant_id"])
    op.create_index("ix_finance_payments_transaction_id", "finance_payments", ["transaction_id"])

    op.execute("ALTER TABLE finance_payments ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE finance_payments FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY tenant_isolation_finance_payments ON finance_payments
        USING (tenant_id::text = current_setting('app.current_tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true))
        """
    )

    # Migra o estado "já pago" existente ANTES de apagar a coluna —
    # nenhuma despesa que já estava marcada como paga perde essa
    # informação, ela vira um pagamento de verdade.
    op.execute(
        """
        INSERT INTO finance_payments (id, tenant_id, transaction_id, created_by_user_id, amount, paid_at)
        SELECT gen_random_uuid(), tenant_id, id, created_by_user_id, amount, occurred_at
        FROM finance_transactions
        WHERE payment_status = 'pago' AND type = 'despesa'
        """
    )

    op.drop_column("finance_transactions", "payment_status")


def downgrade() -> None:
    op.add_column(
        "finance_transactions",
        sa.Column("payment_status", sa.String(20), nullable=False, server_default="pago"),
    )

    # Downgrade só recupera um status BINÁRIO aproximado: se a soma dos
    # pagamentos já cobre o valor lançado, volta como "pago"; senão,
    # "pendente" — perde a granularidade de "parcial" e o histórico de
    # pagamentos em si (a tabela é dropada). Downgrade nunca é sem custo
    # quando a migração original muda o modelo de dados, não só adiciona
    # um campo.
    op.execute(
        """
        UPDATE finance_transactions ft
        SET payment_status = CASE
            WHEN COALESCE((SELECT SUM(amount) FROM finance_payments WHERE transaction_id = ft.id), 0) >= ft.amount
            THEN 'pago'
            ELSE 'pendente'
        END
        WHERE ft.type = 'despesa'
        """
    )

    op.execute("DROP POLICY IF EXISTS tenant_isolation_finance_payments ON finance_payments")
    op.drop_index("ix_finance_payments_transaction_id", table_name="finance_payments")
    op.drop_index("ix_finance_payments_tenant_id", table_name="finance_payments")
    op.drop_table("finance_payments")
