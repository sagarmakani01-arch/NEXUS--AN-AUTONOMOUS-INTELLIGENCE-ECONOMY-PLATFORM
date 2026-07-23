"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("is_active", sa.String(10), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "professions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("proficiency_levels", sa.Integer, server_default="5"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("profession_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professions.id"), nullable=True),
        sa.Column("personality_profile", postgresql.JSON, server_default="{}"),
        sa.Column("reputation", sa.Float, server_default="0.0"),
        sa.Column("current_goal", sa.Text, nullable=True),
        sa.Column("current_status", sa.String(50), server_default="idle"),
        sa.Column("energy", sa.Integer, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id"), unique=True, nullable=False),
        sa.Column("balance", sa.Float, server_default="0.0"),
        sa.Column("currency", sa.String(10), server_default="NXC"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_skills",
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id"), primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id"), primary_key=True),
    )

    op.create_table(
        "memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("memory_type", sa.String(50), server_default="episodic"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("context", postgresql.JSON, server_default="{}"),
        sa.Column("importance", sa.String(20), server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("required_skills", postgresql.JSON, server_default="[]"),
        sa.Column("reward", sa.Integer, server_default="0"),
        sa.Column("status", sa.String(50), server_default="open"),
        sa.Column("priority", sa.String(20), server_default="medium"),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "agent_tasks",
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id"), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), primary_key=True),
    )

    op.create_table(
        "marketplace_listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("seller_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("listing_type", sa.String(50), server_default="service"),
        sa.Column("price", sa.Float, server_default="0.0"),
        sa.Column("required_skills", postgresql.JSON, server_default="[]"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("quantity", sa.Integer, server_default="1"),
        sa.Column("metadata", postgresql.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("treasury_balance", sa.Float, server_default="0.0"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("member_agent_ids", postgresql.JSON, server_default="[]"),
        sa.Column("metadata", postgresql.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("from_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id"), nullable=True),
        sa.Column("to_wallet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wallets.id"), nullable=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), server_default="NXC"),
        sa.Column("transaction_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="completed"),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "event_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", sa.String(255), nullable=False, index=True),
        sa.Column("event_type", sa.String(100), nullable=False, index=True),
        sa.Column("payload", postgresql.JSON, server_default="{}"),
        sa.Column("status", sa.String(50), server_default="logged"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("event_logs")
    op.drop_table("transactions")
    op.drop_table("companies")
    op.drop_table("marketplace_listings")
    op.drop_table("agent_tasks")
    op.drop_table("tasks")
    op.drop_table("memories")
    op.drop_table("agent_skills")
    op.drop_table("wallets")
    op.drop_table("agents")
    op.drop_table("skills")
    op.drop_table("professions")
    op.drop_table("users")
