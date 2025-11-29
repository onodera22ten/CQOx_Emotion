"""add evaluation context fields, trait profile, and path summary tables"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202402070001"
down_revision = "202402060001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("emotion_episode", sa.Column("eval_threat_level", sa.Integer(), nullable=True))
    op.add_column("emotion_episode", sa.Column("suppress_intent_level", sa.Integer(), nullable=True))

    op.create_table(
        "emotion_trait_profile",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("trait_social_anxiety", sa.Integer(), nullable=False),
        sa.Column("trait_crying_proneness", sa.Integer(), nullable=False),
        sa.Column("trait_suppression", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "emotion_path_summary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("alpha_eval_to_stress", sa.Float(), nullable=True),
        sa.Column("beta_eval_to_cry", sa.Float(), nullable=True),
        sa.Column("beta_stress_to_cry", sa.Float(), nullable=True),
        sa.Column("beta_suppress_to_cry", sa.Float(), nullable=True),
        sa.Column("indirect_eval_to_cry", sa.Float(), nullable=True),
        sa.Column("total_eval_to_cry", sa.Float(), nullable=True),
        sa.Column("n_episodes", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("emotion_path_summary")
    op.drop_table("emotion_trait_profile")
    op.drop_column("emotion_episode", "suppress_intent_level")
    op.drop_column("emotion_episode", "eval_threat_level")
