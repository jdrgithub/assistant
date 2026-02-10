"""Second brain schema additions

Revision ID: 002_second_brain
Revises: 001_initial
Create Date: 2026-02-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002_second_brain"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "category_schemas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("fields", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_category_schemas_id"), "category_schemas", ["id"], unique=False)
    op.create_index(op.f("ix_category_schemas_name"), "category_schemas", ["name"], unique=True)

    op.create_table(
        "capture_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("suggested_category", sa.String(), nullable=True),
        sa.Column("suggested_fields", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capture_items_id"), "capture_items", ["id"], unique=False)

    op.create_table(
        "structured_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["category_schemas.id"]),
        sa.ForeignKeyConstraint(["capture_id"], ["capture_items.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_structured_entries_id"), "structured_entries", ["id"], unique=False)

    op.create_table(
        "ingestion_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("details", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["capture_id"], ["capture_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingestion_logs_id"), "ingestion_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingestion_logs_id"), table_name="ingestion_logs")
    op.drop_table("ingestion_logs")
    op.drop_index(op.f("ix_structured_entries_id"), table_name="structured_entries")
    op.drop_table("structured_entries")
    op.drop_index(op.f("ix_capture_items_id"), table_name="capture_items")
    op.drop_table("capture_items")
    op.drop_index(op.f("ix_category_schemas_name"), table_name="category_schemas")
    op.drop_index(op.f("ix_category_schemas_id"), table_name="category_schemas")
    op.drop_table("category_schemas")
