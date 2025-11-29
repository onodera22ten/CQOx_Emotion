"""Initial Emotion CQOx schema"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "202402060001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    scenario_type = sa.Enum(
        "interview",
        "one_on_one",
        "partner",
        "family",
        "friend",
        "client",
        "other",
        name="scenariotype",
    )
    episode_status = sa.Enum("planned", "completed", "cancelled", name="episodestatus")
    partner_reaction = sa.Enum(
        "very_positive",
        "positive",
        "neutral",
        "negative",
        "very_negative",
        "unknown",
        name="partnerreaction",
    )
    scenario_type.create(op.get_bind(), checkfirst=True)
    episode_status.create(op.get_bind(), checkfirst=True)
    partner_reaction.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "emotion_episode",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_type", scenario_type, nullable=False),
        sa.Column("topic", sa.String(length=128), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(length=64), nullable=False),
        sa.Column("status", episode_status, nullable=False),
        sa.Column("pre_anxiety", sa.Integer(), nullable=False),
        sa.Column("pre_crying_risk", sa.Integer(), nullable=False),
        sa.Column("pre_speech_block_risk", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emotion_episode_user_id"), "emotion_episode", ["user_id"], unique=False)

    op.create_table(
        "emotion_preparation_execution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("episode_id", sa.Integer(), nullable=False),
        sa.Column("template_key", sa.String(length=64), nullable=False),
        sa.Column("planned_intensity", sa.Integer(), nullable=False),
        sa.Column("actual_intensity", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["emotion_episode.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_emotion_preparation_execution_episode_id"),
        "emotion_preparation_execution",
        ["episode_id"],
        unique=False,
    )

    op.create_table(
        "emotion_outcome",
        sa.Column("episode_id", sa.Integer(), nullable=False),
        sa.Column("stress_during", sa.Integer(), nullable=False),
        sa.Column("stress_after", sa.Integer(), nullable=False),
        sa.Column("crying_level", sa.Integer(), nullable=False),
        sa.Column("speech_block_level", sa.Integer(), nullable=False),
        sa.Column("expression_score", sa.Integer(), nullable=False),
        sa.Column("relationship_impact", sa.Integer(), nullable=False),
        sa.Column("partner_reaction", partner_reaction, nullable=True),
        sa.Column("days_after_reflection", sa.Integer(), nullable=True),
        sa.Column("would_repeat_preparation", sa.Integer(), nullable=True),
        sa.Column("reflection_short", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["emotion_episode.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("episode_id"),
    )

    op.create_table(
        "emotion_preference_profile",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("weight_relief", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("weight_expression", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("weight_relationship", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "emotion_treatment_effect",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("treatment_key", sa.String(length=64), nullable=False),
        sa.Column("outcome_name", sa.String(length=64), nullable=False),
        sa.Column("ate", sa.Float(), nullable=False),
        sa.Column("ci_lower", sa.Float(), nullable=True),
        sa.Column("ci_upper", sa.Float(), nullable=True),
        sa.Column("n_treated", sa.Integer(), nullable=False),
        sa.Column("n_control", sa.Integer(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "treatment_key", "outcome_name", name="uq_treatment_effect"),
    )
    op.create_index(
        op.f("ix_emotion_treatment_effect_user_id"),
        "emotion_treatment_effect",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "emotion_safety_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("trigger_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("detected_text_hash", sa.String(length=64), nullable=False),
        sa.Column("source_entity", sa.String(length=64), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emotion_safety_log_user_id"), "emotion_safety_log", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_emotion_safety_log_user_id"), table_name="emotion_safety_log")
    op.drop_table("emotion_safety_log")
    op.drop_index(op.f("ix_emotion_treatment_effect_user_id"), table_name="emotion_treatment_effect")
    op.drop_table("emotion_treatment_effect")
    op.drop_table("emotion_preference_profile")
    op.drop_table("emotion_outcome")
    op.drop_index(op.f("ix_emotion_preparation_execution_episode_id"), table_name="emotion_preparation_execution")
    op.drop_table("emotion_preparation_execution")
    op.drop_index(op.f("ix_emotion_episode_user_id"), table_name="emotion_episode")
    op.drop_table("emotion_episode")
    sa.Enum(name="partnerreaction").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="episodestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="scenariotype").drop(op.get_bind(), checkfirst=True)

