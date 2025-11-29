"""
Pydantic schemas for the Emotion CQOx API.

The schemas map closely to the PDF specification: Layer A/B/C inputs,
episode CRUD, outcome logging, analytics, and dashboard payloads.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ---------------------------------------------------------------------------
# Shared enums
# ---------------------------------------------------------------------------


class ScenarioType(str, Enum):
    INTERVIEW = "interview"
    ONE_ON_ONE = "one_on_one"
    PARTNER = "partner"
    FAMILY = "family"
    FRIEND = "friend"
    CLIENT = "client"
    OTHER = "other"


class EpisodeStatus(str, Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PartnerReaction(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Layer A/B/C inputs
# ---------------------------------------------------------------------------


class PreState(BaseModel):
    pre_anxiety: int = Field(..., ge=0, le=10)
    pre_crying_risk: int = Field(..., ge=0, le=10)
    pre_speech_block_risk: int = Field(..., ge=0, le=10)


class PreparationPlan(BaseModel):
    journaling_10m: int = Field(0, ge=0, le=10)
    three_messages: int = Field(0, ge=0, le=10)
    breathing_4_7_8: int = Field(0, ge=0, le=10)
    roleplay_self_qa: int = Field(0, ge=0, le=10)
    safe_word_plan: int = Field(0, ge=0, le=10)


class PreferenceWeightsRaw(BaseModel):
    relief: int = Field(..., ge=0, le=10)
    expression: int = Field(..., ge=0, le=10)
    relationship: int = Field(..., ge=0, le=10)

    @field_validator("relief", "expression", "relationship")
    @classmethod
    def ensure_bounds(cls, v: int) -> int:
        if v < 0 or v > 10:
            raise ValueError("value must be within 0-10")
        return v

    def normalized(self) -> Dict[str, float]:
        total = max(self.relief + self.expression + self.relationship, 1)
        return {
            "relief": self.relief / total,
            "expression": self.expression / total,
            "relationship": self.relationship / total,
        }


class EpisodeDraftCreate(BaseModel):
    scenario_type: ScenarioType
    topic: str
    scheduled_at: datetime
    location: str
    pre_state: PreState
    preparations_planned: PreparationPlan
    preference_weights_raw: PreferenceWeightsRaw


class EpisodeDraftRead(BaseModel):
    episode_id: int
    normalized_weights: Dict[str, float]
    message: str = "Episode draft saved successfully"


# ---------------------------------------------------------------------------
# Episodes & preparations
# ---------------------------------------------------------------------------


class EpisodeRead(BaseModel):
    id: int
    status: EpisodeStatus
    scenario_type: ScenarioType
    topic: str
    scheduled_at: datetime
    location: str
    pre_anxiety: int
    pre_crying_risk: int
    pre_speech_block_risk: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreparationExecutionRead(BaseModel):
    id: int
    episode_id: int
    template_key: str
    planned_intensity: int
    actual_intensity: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PreparationExecutionCreate(BaseModel):
    template_key: str
    planned_intensity: int = Field(..., ge=0, le=10)
    actual_intensity: Optional[int] = Field(None, ge=0, le=10)


# ---------------------------------------------------------------------------
# Outcome schemas
# ---------------------------------------------------------------------------


class OutcomeCreate(BaseModel):
    stress_during: int = Field(..., ge=0, le=10)
    stress_after: int = Field(..., ge=0, le=10)
    crying_level: int = Field(..., ge=0, le=10)
    speech_block_level: int = Field(..., ge=0, le=10)
    expression_score: int = Field(..., ge=0, le=10)
    relationship_impact: int = Field(..., ge=-5, le=5)
    partner_reaction: Optional[PartnerReaction] = None
    days_after_reflection: Optional[int] = Field(None, ge=0, le=30)
    would_repeat_preparation: Optional[int] = Field(None, ge=0, le=10)
    reflection_short: Optional[str] = None


class OutcomeRead(BaseModel):
    episode_id: int
    stress_during: int
    stress_after: int
    crying_level: int
    speech_block_level: int
    expression_score: int
    relationship_impact: int
    partner_reaction: Optional[PartnerReaction]
    days_after_reflection: Optional[int]
    would_repeat_preparation: Optional[int]
    reflection_short: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EpisodeComplete(BaseModel):
    episode: EpisodeRead
    preparations: List[PreparationExecutionRead]
    outcome: Optional[OutcomeRead]


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------


class PreferenceProfileCreate(BaseModel):
    weight_relief: float = Field(..., ge=0, le=1)
    weight_expression: float = Field(..., ge=0, le=1)
    weight_relationship: float = Field(..., ge=0, le=1)

    @field_validator("weight_relief", "weight_expression", "weight_relationship")
    @classmethod
    def _normalize(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("weight must be within 0-1")
        return v


class PreferenceProfileRead(BaseModel):
    user_id: int
    weight_relief: float
    weight_expression: float
    weight_relationship: float
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Analytics / dashboard
# ---------------------------------------------------------------------------


class DeltaMetric(BaseModel):
    mean: float
    ci95: List[float]


class TreatmentEffectRead(BaseModel):
    treatment_key: str
    outcome_name: str
    ate: float
    ci_lower: Optional[float]
    ci_upper: Optional[float]
    n_treated: int
    n_control: int
    model_version: str

    class Config:
        from_attributes = True


class TreatmentEffectList(BaseModel):
    effects: List[TreatmentEffectRead]


class TimelinePoint(BaseModel):
    episode_id: int
    label: str
    crying_level: int
    expression_score: int
    relationship_impact: int


class TimelineResponse(BaseModel):
    points: List[TimelinePoint]


class PreparationCount(BaseModel):
    template_key: str
    count: int


class DashboardSummary(BaseModel):
    by_preparation: List[PreparationCount]
    total_episodes: int
    total_completed: int
    total_planned: int


# ---------------------------------------------------------------------------
# Safety + simulation
# ---------------------------------------------------------------------------


class SafetyCheckRequest(BaseModel):
    text: str


class SafetyResource(BaseModel):
    name: str
    phone: Optional[str] = None
    url: Optional[str] = None
    description: str


class SafetyCheckResponse(BaseModel):
    is_safe: bool
    risk_level: str
    triggers: List[str]
    message: Optional[str] = None
    resources: List[SafetyResource]


class SimulationRequest(BaseModel):
    pre_anxiety: int = Field(..., ge=0, le=10)
    pre_crying_risk: int = Field(..., ge=0, le=10)
    pre_speech_block_risk: int = Field(..., ge=0, le=10)
    prep_journaling_10m: int = Field(0, ge=0, le=10)
    prep_three_messages: int = Field(0, ge=0, le=10)
    prep_breathing_4_7_8: int = Field(0, ge=0, le=10)
    prep_roleplay_self_qa: int = Field(0, ge=0, le=10)
    prep_safe_word_plan: int = Field(0, ge=0, le=10)


class SimulationResponse(BaseModel):
    predicted_stress_after: DeltaMetric
    predicted_crying_level: DeltaMetric
    predicted_expression_score: DeltaMetric
    predicted_relationship_impact: DeltaMetric
    total_reward: float
    disclaimer: str


# ---------------------------------------------------------------------------
# CSV import/export
# ---------------------------------------------------------------------------


class CSVImportRequest(BaseModel):
    file_path: Optional[str] = None


class CSVImportResponse(BaseModel):
    imported_count: int
    errors: List[str]
    warnings: List[str]
