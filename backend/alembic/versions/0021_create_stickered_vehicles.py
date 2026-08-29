"""cria tabela stickered_vehicles com RLS

Revision ID: 0021_create_stickered_vehicles
Revises: 0020_add_finance_attachment
Create Date: 2026-08-19

Veículo adesivado — proprietário pode ser um Voter já cadastrado
(voter_id, opcional) ou só um nome livre (owner_name, sempre
obrigatório). ON DELETE SET NULL no voter_id: se o eleitor vinculado for
excluído, o registro do veículo continua existindo (só perde o vínculo).
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_create_stickered_vehicles"
down_revision: str | None = "0020_add_finance_attachment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stickered_vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("plate", sa.String(10), nullable=False),
        sa.Column("owner_name", sa.String(255), nullable=False),
        sa.Column(
            "voter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("voters.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("stickered_at", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("photo_storage_key", sa.String(500), nullable=True),
        sa.Column("photo_filename", sa.String(255), nullable=True),
        sa.Column("photo_content_type", sa.String(100), nullable=True),
        sa.Column("photo_size_bytes", sa.BigInteger(), nullable=True),
    )

    op.create_index("ix_stickered_vehicles_tenant_id", "stickered_vehicles", ["tenant_id"])
    op.create_index("ix_stickered_vehicles_plate", "stickered_vehicles", ["plate"])

    op.execute("ALTER TABLE stickered_vehicles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE stickered_vehicles FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY tenant_isolation_stickered_vehicles ON stickered_vehicles
        USING (tenant_id::text = current_setting('app.current_tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.current_tenant_id', true))
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_stickered_vehicles ON stickered_vehicles")
    op.drop_index("ix_stickered_vehicles_plate", table_name="stickered_vehicles")
    op.drop_index("ix_stickered_vehicles_tenant_id", table_name="stickered_vehicles")
    op.drop_table("stickered_vehicles")
