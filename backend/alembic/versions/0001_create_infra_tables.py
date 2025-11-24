"""create infra tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "infra_tickets",
        sa.Column("ticket_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("workstation", sa.String(length=100), nullable=True),
        sa.Column("status", sa.Enum("New", "Assigned", "In Progress", "On Hold", "Resolved", name="status_enum"), nullable=False, server_default="New"),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("commitment_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_delayed_pick", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_invalid", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("invalid_reason", sa.Text(), nullable=True),
        sa.Column("image_path", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "infra_updates",
        sa.Column("update_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("infra_tickets.ticket_id", ondelete="CASCADE"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_status", "infra_tickets", ["status"])
    op.create_index("idx_created_at", "infra_tickets", ["created_at"])
    op.create_index("idx_department", "infra_tickets", ["department"])
    op.create_index("idx_assigned_to", "infra_tickets", ["assigned_to"])
    op.create_index("idx_delayed", "infra_tickets", ["is_delayed_pick"])


def downgrade():
    op.drop_index("idx_delayed", table_name="infra_tickets")
    op.drop_index("idx_assigned_to", table_name="infra_tickets")
    op.drop_index("idx_department", table_name="infra_tickets")
    op.drop_index("idx_created_at", table_name="infra_tickets")
    op.drop_index("idx_status", table_name="infra_tickets")
    op.drop_table("infra_updates")
    op.drop_table("infra_tickets")
