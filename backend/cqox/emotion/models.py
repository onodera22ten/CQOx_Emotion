"""
SQLAlchemy models for the Emotion CQOx domain.

The structures intentionally mirror the PDF specification:
- EmotionEpisode: core log row
- EmotionPreparationExecution: planned/actual intensities
- EmotionOutcome: outcome + reflection (post episode)
- EmotionPreferenceProfile: Layer-B preference weights
- EmotionTreatmentEffect: persisted ATEs from the causal job
"""
from __future__ import annotations

from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cqox.db import Base


class ScenarioType(str, enum.Enum):
    INTERVIEW = "interview"
    ONE_ON_ONE = "one_on_one"
    PARTNER = "partner"
    FAMILY = "family"
    FRIEND = "friend"
    CLIENT = "client"
    OTHER = "other"


class EpisodeStatus(str, enum.Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PartnerReaction(str, enum.Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    UNKNOWN = "unknown"


class EmotionEpisode(Base):
    """Core episode log."""

    __tablename__ = "emotion_episode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    scenario_type: Mapped[ScenarioType] = mapped_column(SQLEnum(ScenarioType), nullable=False)
    topic: Mapped[str] = mapped_column(String(128), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[EpisodeStatus] = mapped_column(SQLEnum(EpisodeStatus), nullable=False, default=EpisodeStatus.PLANNED)
    pre_anxiety: Mapped[int] = mapped_column(Integer, nullable=False)
    pre_crying_risk: Mapped[int] = mapped_column(Integer, nullable=False)
    pre_speech_block_risk: Mapped[int] = mapped_column(Integer, nullable=False)
    eval_threat_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suppress_intent_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_partner_role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    context_formality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_self_disclosure: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_eval_focus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    preparations: Mapped[list["EmotionPreparationExecution"]] = relationship(
        "EmotionPreparationExecution", back_populates="episode", cascade="all, delete-orphan"
    )
    outcome: Mapped["EmotionOutcome"] = relationship(
        "EmotionOutcome", back_populates="episode", uselist=False, cascade="all, delete-orphan"
    )


class EmotionPreparationExecution(Base):
    """Preparation entries (planned vs actual)."""

    __tablename__ = "emotion_preparation_execution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey("emotion_episode.id", ondelete="CASCADE"), index=True, nullable=False)
    template_key: Mapped[str] = mapped_column(String(64), nullable=False)
    planned_intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_intensity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    episode: Mapped[EmotionEpisode] = relationship("EmotionEpisode", back_populates="preparations")


class EmotionOutcome(Base):
    """Outcome metrics and lightweight reflection."""

    __tablename__ = "emotion_outcome"

    episode_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("emotion_episode.id", ondelete="CASCADE"), primary_key=True
    )
    stress_during: Mapped[int] = mapped_column(Integer, nullable=False)
    stress_after: Mapped[int] = mapped_column(Integer, nullable=False)
    crying_level: Mapped[int] = mapped_column(Integer, nullable=False)
    speech_block_level: Mapped[int] = mapped_column(Integer, nullable=False)
    expression_score: Mapped[int] = mapped_column(Integer, nullable=False)
    relationship_impact: Mapped[int] = mapped_column(Integer, nullable=False)
    partner_reaction: Mapped[PartnerReaction | None] = mapped_column(SQLEnum(PartnerReaction), nullable=True)
    days_after_reflection: Mapped[int | None] = mapped_column(Integer, nullable=True)
    would_repeat_preparation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reflection_short: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    episode: Mapped[EmotionEpisode] = relationship("EmotionEpisode", back_populates="outcome")


class EmotionPreferenceProfile(Base):
    """Layer-B preference weights per user."""

    __tablename__ = "emotion_preference_profile"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    weight_relief: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    weight_expression: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    weight_relationship: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmotionTreatmentEffect(Base):
    """Persisted per-user ATEs estimated by the batch job."""

    __tablename__ = "emotion_treatment_effect"
    __table_args__ = (
        UniqueConstraint("user_id", "treatment_key", "outcome_name", name="uq_treatment_effect"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    treatment_key: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome_name: Mapped[str] = mapped_column(String(64), nullable=False)
    ate: Mapped[float] = mapped_column(Float, nullable=False)
    ci_lower: Mapped[float | None] = mapped_column(Float, nullable=True)
    ci_upper: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_treated: Mapped[int] = mapped_column(Integer, nullable=False)
    n_control: Mapped[int] = mapped_column(Integer, nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SafetyLog(Base):
    """Optional log for safety guard triggers."""

    __tablename__ = "emotion_safety_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    detected_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_entity: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class EmotionTraitProfile(Base):
    """User trait profile (baseline social anxiety / crying proneness / suppression)."""

    __tablename__ = "emotion_trait_profile"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trait_social_anxiety: Mapped[int] = mapped_column(Integer, nullable=False)
    trait_crying_proneness: Mapped[int] = mapped_column(Integer, nullable=False)
    trait_suppression: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmotionPathSummary(Base):
    """Persisted per-user path summary for evaluation -> crying model."""

    __tablename__ = "emotion_path_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    intercept: Mapped[float | None] = mapped_column(Float, nullable=True)
    intercept_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    intercept_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    alpha_eval_to_stress: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_eval_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_stress_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_suppress_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_trait_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    indirect_eval_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_eval_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_trait_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_trait_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    alpha_eval_to_stress_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    alpha_eval_to_stress_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_eval_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_eval_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_stress_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_stress_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_suppress_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    beta_suppress_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    indirect_eval_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    indirect_eval_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_eval_to_cry_lo: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_eval_to_cry_hi: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_episodes: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmotionPathPartnerSummary(Base):
    """Partner-role specific evaluation path summary."""

    __tablename__ = "emotion_path_partner_summary"
    __table_args__ = (
        UniqueConstraint("user_id", "partner_role", name="uq_path_partner"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    partner_role: Mapped[str] = mapped_column(String(32), nullable=False)
    total_eval_to_cry: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_episodes: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
