"""create posts comments likes tables

Revision ID: 20260412_0003
Revises: 20260412_0002
Create Date: 2026-04-12 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260412_0003"
down_revision: Union[str, None] = "20260412_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("comment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_posts_user_id", "posts", ["user_id"], unique=False)
    op.create_index("idx_posts_created_at", "posts", ["created_at"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "post_id",
            sa.Integer(),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("comments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_comments_post_id", "comments", ["post_id"], unique=False)
    op.create_index("idx_comments_user_id", "comments", ["user_id"], unique=False)
    op.create_index("idx_comments_parent_id", "comments", ["parent_id"], unique=False)
    op.create_index("idx_comments_created_at", "comments", ["created_at"], unique=False)

    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "post_id",
            sa.Integer(),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("user_id", "post_id", name="uk_likes_user_post"),
        mysql_charset="utf8mb4",
    )
    op.create_index("idx_likes_user_id", "likes", ["user_id"], unique=False)
    op.create_index("idx_likes_post_id", "likes", ["post_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_likes_post_id", table_name="likes")
    op.drop_index("idx_likes_user_id", table_name="likes")
    op.drop_table("likes")

    op.drop_index("idx_comments_created_at", table_name="comments")
    op.drop_index("idx_comments_parent_id", table_name="comments")
    op.drop_index("idx_comments_user_id", table_name="comments")
    op.drop_index("idx_comments_post_id", table_name="comments")
    op.drop_table("comments")

    op.drop_index("idx_posts_created_at", table_name="posts")
    op.drop_index("idx_posts_user_id", table_name="posts")
    op.drop_table("posts")
