"""create bird records table

Revision ID: 20260412_0002
Revises: 20260324_0001
Create Date: 2026-04-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260412_0002"
down_revision: Union[str, None] = "20260324_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bird_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bird_name", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_bird_records_user_id", "bird_records", ["user_id"], unique=False)
    op.create_index(
        "idx_bird_records_created_at", "bird_records", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_bird_records_created_at", table_name="bird_records")
    op.drop_index("idx_bird_records_user_id", table_name="bird_records")
    op.drop_table("bird_records")
