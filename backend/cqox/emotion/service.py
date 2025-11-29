"""
Service layer functions for Emotion CQOx.

We separate business logic from FastAPI endpoints to keep the routers thin
and make the logic easier to test.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas
from cqox.jobs.estimate_effects import estimate_and_persist_effects

logger = logging.getLogger(__name__)

PREPARATION_TEMPLATE_KEYS = [
    "journaling_10m",
    "three_messages",
    "breathing_4_7_8",
    "roleplay_self_qa",
    "safe_word_plan",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _prep_intensity_map(plan: schemas.PreparationPlan) -> dict[str, int]:
    return {
        "journaling_10m": plan.journaling_10m,
        "three_messages": plan.three_messages,
        "breathing_4_7_8": plan.breathing_4_7_8,
        "roleplay_self_qa": plan.roleplay_self_qa,
        "safe_word_plan": plan.safe_word_plan,
    }


def _upsert_preference_profile(db: Session, user_id: int, weights: dict[str, float]) -> models.EmotionPreferenceProfile:
    profile = db.query(models.EmotionPreferenceProfile).filter_by(user_id=user_id).first()
    now = datetime.utcnow()

    if profile:
        profile.weight_relief = weights["relief"]
        profile.weight_expression = weights["expression"]
        profile.weight_relationship = weights["relationship"]
        profile.updated_at = now
    else:
        profile = models.EmotionPreferenceProfile(
            user_id=user_id,
            weight_relief=weights["relief"],
            weight_expression=weights["expression"],
            weight_relationship=weights["relationship"],
            updated_at=now,
        )
        db.add(profile)

    return profile


# ---------------------------------------------------------------------------
# Episode flows
# ---------------------------------------------------------------------------


def create_episode_draft(db: Session, user_id: int, draft: schemas.EpisodeDraftCreate) -> schemas.EpisodeDraftRead:
    """Create an episode plus planned preparations."""
    episode = models.EmotionEpisode(
        user_id=user_id,
        scenario_type=draft.scenario_type,
        topic=draft.topic,
        scheduled_at=draft.scheduled_at,
        location=draft.location,
        status=models.EpisodeStatus.PLANNED,
        pre_anxiety=draft.pre_state.pre_anxiety,
        pre_crying_risk=draft.pre_state.pre_crying_risk,
        pre_speech_block_risk=draft.pre_state.pre_speech_block_risk,
    )
    db.add(episode)
    db.flush()

    for template_key, intensity in _prep_intensity_map(draft.preparations_planned).items():
        if intensity <= 0:
            continue
        db.add(
            models.EmotionPreparationExecution(
                episode_id=episode.id,
                template_key=template_key,
                planned_intensity=intensity,
            )
        )

    normalized = draft.preference_weights_raw.normalized()
    _upsert_preference_profile(db, user_id, normalized)

    db.commit()
    db.refresh(episode)

    return schemas.EpisodeDraftRead(
        episode_id=episode.id,
        normalized_weights=normalized,
        message=f"Episode draft saved successfully (ID: {episode.id})",
    )


def list_episodes(
    db: Session,
    user_id: int,
    status: Optional[models.EpisodeStatus] = None,
    limit: int = 50,
) -> List[schemas.EpisodeRead]:
    query = db.query(models.EmotionEpisode).filter(models.EmotionEpisode.user_id == user_id)
    if status:
        query = query.filter(models.EmotionEpisode.status == status)
    episodes = query.order_by(models.EmotionEpisode.scheduled_at.desc()).limit(limit).all()
    return [schemas.EpisodeRead.model_validate(ep) for ep in episodes]


def get_episode_detail(db: Session, user_id: int, episode_id: int) -> schemas.EpisodeComplete:
    episode = (
        db.query(models.EmotionEpisode)
        .filter(models.EmotionEpisode.id == episode_id, models.EmotionEpisode.user_id == user_id)
        .first()
    )
    if not episode:
        raise ValueError("Episode not found")
    preparations = db.query(models.EmotionPreparationExecution).filter_by(episode_id=episode_id).all()
    outcome = db.query(models.EmotionOutcome).filter_by(episode_id=episode_id).first()
    return schemas.EpisodeComplete(
        episode=schemas.EpisodeRead.model_validate(episode),
        preparations=[schemas.PreparationExecutionRead.model_validate(p) for p in preparations],
        outcome=schemas.OutcomeRead.model_validate(outcome) if outcome else None,
    )


def add_preparation_execution(
    db: Session,
    user_id: int,
    episode_id: int,
    payload: schemas.PreparationExecutionCreate,
) -> schemas.PreparationExecutionRead:
    episode = (
        db.query(models.EmotionEpisode)
        .filter(models.EmotionEpisode.id == episode_id, models.EmotionEpisode.user_id == user_id)
        .first()
    )
    if not episode:
        raise ValueError("Episode not found")

    execution = models.EmotionPreparationExecution(
        episode_id=episode_id,
        template_key=payload.template_key,
        planned_intensity=payload.planned_intensity,
        actual_intensity=payload.actual_intensity,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return schemas.PreparationExecutionRead.model_validate(execution)


def record_outcome(db: Session, user_id: int, episode_id: int, outcome: schemas.OutcomeCreate) -> schemas.OutcomeRead:
    episode = (
        db.query(models.EmotionEpisode)
        .filter(models.EmotionEpisode.id == episode_id, models.EmotionEpisode.user_id == user_id)
        .first()
    )
    if not episode:
        raise ValueError("Episode not found")
    if episode.outcome:
        raise ValueError("Outcome already recorded")

    outcome_record = models.EmotionOutcome(
        episode_id=episode_id,
        stress_during=outcome.stress_during,
        stress_after=outcome.stress_after,
        crying_level=outcome.crying_level,
        speech_block_level=outcome.speech_block_level,
        expression_score=outcome.expression_score,
        relationship_impact=outcome.relationship_impact,
        partner_reaction=outcome.partner_reaction,
        days_after_reflection=outcome.days_after_reflection,
        would_repeat_preparation=outcome.would_repeat_preparation,
        reflection_short=outcome.reflection_short,
    )
    db.add(outcome_record)
    episode.status = models.EpisodeStatus.COMPLETED
    db.commit()
    db.refresh(outcome_record)

    try:
        estimate_and_persist_effects()
    except Exception:
        logger.exception("Failed to run treatment effect estimation job")

    return schemas.OutcomeRead.model_validate(outcome_record)


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------


def get_preference_profile(db: Session, user_id: int) -> schemas.PreferenceProfileRead:
    profile = db.query(models.EmotionPreferenceProfile).filter_by(user_id=user_id).first()
    if not profile:
        profile = models.EmotionPreferenceProfile(
            user_id=user_id,
            weight_relief=0.33,
            weight_expression=0.33,
            weight_relationship=0.34,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return schemas.PreferenceProfileRead.model_validate(profile)


def update_preference_profile(
    db: Session, user_id: int, payload: schemas.PreferenceProfileCreate
) -> schemas.PreferenceProfileRead:
    total = payload.weight_relief + payload.weight_expression + payload.weight_relationship
    if total == 0:
        weights = {"relief": 1 / 3, "expression": 1 / 3, "relationship": 1 / 3}
    else:
        weights = {
            "relief": payload.weight_relief / total,
            "expression": payload.weight_expression / total,
            "relationship": payload.weight_relationship / total,
        }
    profile = _upsert_preference_profile(db, user_id, weights)
    db.commit()
    db.refresh(profile)
    return schemas.PreferenceProfileRead.model_validate(profile)


# ---------------------------------------------------------------------------
# Analytics helpers
# ---------------------------------------------------------------------------


def get_treatment_effects_for_user(db: Session, user_id: int) -> List[schemas.TreatmentEffectRead]:
    effects = db.query(models.EmotionTreatmentEffect).filter_by(user_id=user_id).all()
    return [schemas.TreatmentEffectRead.model_validate(eff) for eff in effects]


def get_timeline_points(db: Session, user_id: int) -> schemas.TimelineResponse:
    episodes = (
        db.query(models.EmotionEpisode)
        .join(models.EmotionOutcome)
        .filter(models.EmotionEpisode.user_id == user_id)
        .order_by(models.EmotionEpisode.scheduled_at.asc())
        .all()
    )
    points = []
    for idx, ep in enumerate(episodes, start=1):
        points.append(
            schemas.TimelinePoint(
                episode_id=ep.id,
                label=f"{ep.scenario_type.value} #{idx}",
                crying_level=ep.outcome.crying_level,
                expression_score=ep.outcome.expression_score,
                relationship_impact=ep.outcome.relationship_impact,
            )
        )
    return schemas.TimelineResponse(points=points)


def get_dashboard_summary(db: Session, user_id: int) -> schemas.DashboardSummary:
    total = db.query(func.count(models.EmotionEpisode.id)).filter_by(user_id=user_id).scalar() or 0
    total_completed = (
        db.query(func.count(models.EmotionEpisode.id))
        .filter_by(user_id=user_id, status=models.EpisodeStatus.COMPLETED)
        .scalar()
        or 0
    )
    total_planned = (
        db.query(func.count(models.EmotionEpisode.id))
        .filter_by(user_id=user_id, status=models.EpisodeStatus.PLANNED)
        .scalar()
        or 0
    )

    by_prep = []
    for key in PREPARATION_TEMPLATE_KEYS:
        count = (
            db.query(func.count(models.EmotionPreparationExecution.id))
            .join(models.EmotionEpisode, models.EmotionPreparationExecution.episode_id == models.EmotionEpisode.id)
            .filter(
                models.EmotionEpisode.user_id == user_id,
                models.EmotionPreparationExecution.template_key == key,
            )
            .scalar()
            or 0
        )
        by_prep.append({"template_key": key, "count": count})

    return schemas.DashboardSummary(
        by_preparation=by_prep,
        total_episodes=total,
        total_completed=total_completed,
        total_planned=total_planned,
    )
