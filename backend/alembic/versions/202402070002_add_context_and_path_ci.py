"""add episode context fields and path summary confidence intervals"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "202402070002"
down_revision = "202402070001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("emotion_episode", sa.Column("context_partner_role", sa.String(length=32), nullable=True))
    op.add_column("emotion_episode", sa.Column("context_formality", sa.Integer(), nullable=True))
    op.add_column("emotion_episode", sa.Column("context_self_disclosure", sa.Integer(), nullable=True))
    op.add_column("emotion_episode", sa.Column("context_eval_focus", sa.Integer(), nullable=True))

    op.add_column("emotion_path_summary", sa.Column("intercept", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("intercept_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("intercept_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_trait_to_cry", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_trait_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_trait_to_cry_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("alpha_eval_to_stress_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("alpha_eval_to_stress_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_eval_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_eval_to_cry_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_stress_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_stress_to_cry_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_suppress_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("beta_suppress_to_cry_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("indirect_eval_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("indirect_eval_to_cry_hi", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("total_eval_to_cry_lo", sa.Float(), nullable=True))
    op.add_column("emotion_path_summary", sa.Column("total_eval_to_cry_hi", sa.Float(), nullable=True))

    op.create_table(
        "emotion_path_partner_summary",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("partner_role", sa.String(length=32), nullable=False),
        sa.Column("total_eval_to_cry", sa.Float(), nullable=True),
        sa.Column("n_episodes", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "partner_role", name="uq_path_partner"),
    )


def downgrade() -> None:
    op.drop_table("emotion_path_partner_summary")

    op.drop_column("emotion_path_summary", "total_eval_to_cry_hi")
    op.drop_column("emotion_path_summary", "total_eval_to_cry_lo")
    op.drop_column("emotion_path_summary", "indirect_eval_to_cry_hi")
    op.drop_column("emotion_path_summary", "indirect_eval_to_cry_lo")
    op.drop_column("emotion_path_summary", "beta_suppress_to_cry_hi")
    op.drop_column("emotion_path_summary", "beta_suppress_to_cry_lo")
    op.drop_column("emotion_path_summary", "beta_stress_to_cry_hi")
    op.drop_column("emotion_path_summary", "beta_stress_to_cry_lo")
    op.drop_column("emotion_path_summary", "beta_eval_to_cry_hi")
    op.drop_column("emotion_path_summary", "beta_eval_to_cry_lo")
    op.drop_column("emotion_path_summary", "alpha_eval_to_stress_hi")
    op.drop_column("emotion_path_summary", "alpha_eval_to_stress_lo")
    op.drop_column("emotion_path_summary", "beta_trait_to_cry_hi")
    op.drop_column("emotion_path_summary", "beta_trait_to_cry_lo")
    op.drop_column("emotion_path_summary", "beta_trait_to_cry")
    op.drop_column("emotion_path_summary", "intercept_hi")
    op.drop_column("emotion_path_summary", "intercept_lo")
    op.drop_column("emotion_path_summary", "intercept")

    op.drop_column("emotion_episode", "context_eval_focus")
    op.drop_column("emotion_episode", "context_self_disclosure")
    op.drop_column("emotion_episode", "context_formality")
    op.drop_column("emotion_episode", "context_partner_role")
