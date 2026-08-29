"""cria finance_attachments (múltiplos anexos), migra dados existentes

Revision ID: 0022_finance_multi_attach
Revises: 0021_create_stickered_vehicles
Create Date: 2026-08-25

Antes: um anexo por lançamento, campos soltos em finance_transactions.
Depois: múltiplos anexos por lançamento (até 10, checado na aplicação),
cada um com categoria (comprovante/contrato/orcamento/outro), em tabela
própria.

IMPORTANTE: migra os dados que já existem ANTES de apagar as colunas
antigas — nenhum anexo já cadastrado é perdido. Categoria dos anexos
migrados é sempre "comprovante" (era a única categoria implícita antes
dessa mudança existir).
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_finance_multi_attach"
down_revision: str | None = "0021_create_stickered_vehicles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "finance_attachments",
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
            "uploaded_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_finance_attachments_tenant_id", "finance_attachments", ["tenant_id"])
    op.create_index("ix_finance_attachments_transaction_id", "finance_attachments", ["transaction_id"])

    op.execute("ALTER TABLE finance_attachments ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE finance_attachments FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY tenant_isolation_finance_attachments ON finance_attachments
        USING (tenant_id::text = current_setting('app.current_tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true))
        """
    )

    # Migra qualquer anexo já cadastrado ANTES de apagar as colunas
    # antigas — usa created_by_user_id da transação como
    # uploaded_by_user_id (não tínhamos "quem anexou" separado de "quem
    # criou o lançamento" antes dessa mudança).
    op.execute(
        """
        INSERT INTO finance_attachments
            (id, tenant_id, transaction_id, uploaded_by_user_id, category,
             storage_key, filename, content_type, size_bytes, uploaded_at)
        SELECT
            gen_random_uuid(), tenant_id, id, created_by_user_id, 'comprovante',
            attachment_storage_key, attachment_filename, attachment_content_type,
            attachment_size_bytes, updated_at
        FROM finance_transactions
        WHERE attachment_storage_key IS NOT NULL
        """
    )

    op.drop_column("finance_transactions", "attachment_storage_key")
    op.drop_column("finance_transactions", "attachment_filename")
    op.drop_column("finance_transactions", "attachment_content_type")
    op.drop_column("finance_transactions", "attachment_size_bytes")


def downgrade() -> None:
    op.add_column("finance_transactions", sa.Column("attachment_storage_key", sa.String(500), nullable=True))
    op.add_column("finance_transactions", sa.Column("attachment_filename", sa.String(255), nullable=True))
    op.add_column("finance_transactions", sa.Column("attachment_content_type", sa.String(100), nullable=True))
    op.add_column("finance_transactions", sa.Column("attachment_size_bytes", sa.BigInteger(), nullable=True))

    # Downgrade só recupera UM anexo por lançamento (o mais recente) —
    # essa é uma perda de informação aceitável ao reverter uma migração
    # que expandiu a estrutura; downgrade nunca é "sem custo" quando a
    # migração original é uma mudança de modelo, não só um campo novo.
    op.execute(
        """
        UPDATE finance_transactions ft
        SET attachment_storage_key = fa.storage_key,
            attachment_filename = fa.filename,
            attachment_content_type = fa.content_type,
            attachment_size_bytes = fa.size_bytes
        FROM (
            SELECT DISTINCT ON (transaction_id) *
            FROM finance_attachments
            ORDER BY transaction_id, uploaded_at DESC
        ) fa
        WHERE ft.id = fa.transaction_id
        """
    )

    op.execute("DROP POLICY IF EXISTS tenant_isolation_finance_attachments ON finance_attachments")
    op.drop_index("ix_finance_attachments_transaction_id", table_name="finance_attachments")
    op.drop_index("ix_finance_attachments_tenant_id", table_name="finance_attachments")
    op.drop_table("finance_attachments")
