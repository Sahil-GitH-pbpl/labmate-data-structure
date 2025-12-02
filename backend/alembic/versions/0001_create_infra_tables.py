"""create hiccup module tables

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


def upgrade() -> None:
    op.create_table(
        "department_master",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )
    op.create_table(
        "staff_master",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("staff", "management", "admin", "hod", name="roleenum"), nullable=False, server_default="staff"),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("department_master.id"), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
    )
    op.create_table(
        "system_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_table(
        "hiccups",
        sa.Column("hiccup_id", sa.String(length=20), primary_key=True),
        sa.Column("raised_by", sa.Integer(), sa.ForeignKey("staff_master.id"), nullable=False),
        sa.Column("raised_by_department", sa.Integer(), sa.ForeignKey("department_master.id"), nullable=False),
        sa.Column("hiccup_type", sa.Enum("Person Related", "System Related", name="hiccuptype"), nullable=False),
        sa.Column("raised_against", sa.String(length=255), nullable=False),
        sa.Column("raised_against_department", sa.Integer(), sa.ForeignKey("department_master.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("immediate_effect", sa.Text(), nullable=True),
        sa.Column("attachment_path", sa.String(length=255), nullable=True),
        sa.Column("response_by", sa.Integer(), sa.ForeignKey("staff_master.id"), nullable=True),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("Open", "Responded", "Under Review", "Closed", "Escalated to NC", name="hiccupstatus"),
            nullable=False,
            server_default="Open",
        ),
        sa.Column("escalated_by", sa.Integer(), sa.ForeignKey("staff_master.id"), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        sa.Column("closure_notes", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("is_auto_generated", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("source_module", sa.String(length=255), nullable=True),
        sa.Column("confidential_flag", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "root_cause_category",
            sa.Enum(
                "Training Need",
                "Process Gap",
                "Negligence",
                "System Error",
                "External Factor",
                "Resource Shortage",
                name="rootcausecategory",
            ),
            nullable=True,
        ),
        sa.Column("followup_status", sa.Enum("Pending", "Resolved", "Unresolved", name="followupstatus"), nullable=False, server_default="Pending"),
        sa.Column("followup_comment", sa.Text(), nullable=True),
        sa.Column("followup_due", sa.DateTime(), nullable=True),
        sa.Index("idx_hiccup_status", "status"),
        sa.Index("idx_hiccup_created", "created_at"),
        sa.Index("idx_hiccup_raised_by", "raised_by"),
        sa.Index("idx_hiccup_raised_against", "raised_against"),
        sa.Index("idx_hiccup_source", "source_module"),
    )
    op.create_table(
        "hiccup_audit_log",
        sa.Column("log_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("hiccup_id", sa.String(length=20), sa.ForeignKey("hiccups.hiccup_id"), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("performed_by", sa.Integer(), sa.ForeignKey("staff_master.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("remarks", sa.Text(), nullable=True),
    )
    op.execute("INSERT INTO department_master (id, name) VALUES (1, 'General')")
    op.execute("INSERT INTO staff_master (id, name, role, department_id) VALUES (1, 'System', 'admin', 1)")
    op.execute("INSERT INTO system_tokens (token, description, active) VALUES ('internal-token', 'default', 1)")


def downgrade() -> None:
    op.drop_table("hiccup_audit_log")
    op.drop_table("hiccups")
    op.drop_table("system_tokens")
    op.drop_table("staff_master")
    op.drop_table("department_master")
