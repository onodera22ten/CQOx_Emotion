"""
Emotion CQOx API endpoints.

Routers are intentionally thin; business logic lives inside service.py.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from cqox.dependencies import get_current_user, get_db
from cqox.emotion import service, schemas
from cqox.emotion.analytics import AnalyticsEngine
from cqox.emotion.safety import SafetyGuard

router = APIRouter(prefix="/api/emotion", tags=["emotion"])


@router.post("/episodes/draft", response_model=schemas.EpisodeDraftRead, status_code=status.HTTP_201_CREATED)
def create_episode_draft(
    draft: schemas.EpisodeDraftCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.create_episode_draft(db, current_user["id"], draft)


@router.get("/episodes", response_model=list[schemas.EpisodeRead])
def list_my_episodes(
    status: schemas.EpisodeStatus | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.list_episodes(db, current_user["id"], status=status, limit=limit)


@router.get("/episodes/{episode_id}", response_model=schemas.EpisodeComplete)
def get_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return service.get_episode_detail(db, current_user["id"], episode_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/episodes/{episode_id}/preparations",
    response_model=schemas.PreparationExecutionRead,
    status_code=status.HTTP_201_CREATED,
)
def add_preparation_execution(
    episode_id: int,
    payload: schemas.PreparationExecutionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return service.add_preparation_execution(db, current_user["id"], episode_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/episodes/{episode_id}/outcome", response_model=schemas.OutcomeRead)
def record_outcome(
    episode_id: int,
    outcome: schemas.OutcomeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return service.record_outcome(db, current_user["id"], episode_id, outcome)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.get_dashboard_summary(db, current_user["id"])


@router.get("/effects/me", response_model=schemas.TreatmentEffectList)
def get_my_effects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    effects = service.get_treatment_effects_for_user(db, current_user["id"])
    return schemas.TreatmentEffectList(effects=effects)


@router.get("/episodes/timeline/me", response_model=schemas.TimelineResponse)
def get_my_timeline(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.get_timeline_points(db, current_user["id"])


@router.get("/preferences/me", response_model=schemas.PreferenceProfileRead)
def get_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.get_preference_profile(db, current_user["id"])


@router.post("/preferences/me", response_model=schemas.PreferenceProfileRead)
def update_preferences(
    payload: schemas.PreferenceProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.update_preference_profile(db, current_user["id"], payload)


@router.post("/safety/check", response_model=schemas.SafetyCheckResponse)
def safety_check(
    payload: schemas.SafetyCheckRequest,
    current_user=Depends(get_current_user),
):
    guard = SafetyGuard()
    result = guard.check_text(payload.text)
    # In production we would persist SafetyLog entries here.
    return result


@router.post("/simulate", response_model=schemas.SimulationResponse)
def simulate(
    payload: schemas.SimulationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = AnalyticsEngine()
    preparations = {
        "journaling_10m": payload.prep_journaling_10m,
        "three_messages": payload.prep_three_messages,
        "breathing_4_7_8": payload.prep_breathing_4_7_8,
        "roleplay_self_qa": payload.prep_roleplay_self_qa,
        "safe_word_plan": payload.prep_safe_word_plan,
    }
    prediction = engine.predict_outcome(
        pre_anxiety=payload.pre_anxiety,
        pre_crying_risk=payload.pre_crying_risk,
        pre_speech_block_risk=payload.pre_speech_block_risk,
        preparations=preparations,
    )

    prefs = service.get_preference_profile(db, current_user["id"])
    total_reward = engine.calculate_total_reward(
        predicted_stress_after=prediction["stress_after"]["mean"],
        predicted_expression=prediction["expression_score"]["mean"],
        predicted_relationship=prediction["relationship_impact"]["mean"],
        pre_anxiety=float(payload.pre_anxiety),
        weight_relief=prefs.weight_relief,
        weight_expression=prefs.weight_expression,
        weight_relationship=prefs.weight_relationship,
    )

    return schemas.SimulationResponse(
        predicted_stress_after=schemas.DeltaMetric(**prediction["stress_after"]),
        predicted_crying_level=schemas.DeltaMetric(**prediction["crying_level"]),
        predicted_expression_score=schemas.DeltaMetric(**prediction["expression_score"]),
        predicted_relationship_impact=schemas.DeltaMetric(**prediction["relationship_impact"]),
        total_reward=total_reward,
        disclaimer="これは予測であり、保証ではありません。実際の結果は異なる場合があります。",
    )


@router.post("/import/csv", response_model=schemas.CSVImportResponse)
def import_csv(
    payload: schemas.CSVImportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Placeholder for future implementation
    return schemas.CSVImportResponse(imported_count=0, errors=[], warnings=["Not implemented"])


@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    raise HTTPException(status_code=501, detail="Not implemented yet")
