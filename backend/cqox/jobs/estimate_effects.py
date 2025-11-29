"""
Estimate per-user treatment effects (ATE) and persist them.

This is a simplified Double Machine Learning style estimator,
matching the outline from CQOx_gen 拡張案④.
"""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from cqox.db import session_scope
from cqox.emotion import models

TREATMENTS = [
    "journaling_10m",
    "three_messages",
    "breathing_4_7_8",
    "roleplay_self_qa",
    "safe_word_plan",
]

OUTCOMES = [
    "crying_level",
    "stress_after",
    "expression_score",
    "relationship_impact",
]

MODEL_VERSION = "v1.0-dml"


def load_episode_dataframe(db: Session) -> pd.DataFrame:
    """Load completed episodes with outcomes + preparations into a flat DF."""
    episodes = (
        db.query(models.EmotionEpisode)
        .join(models.EmotionOutcome)
        .filter(models.EmotionEpisode.status == models.EpisodeStatus.COMPLETED)
        .all()
    )
    rows: List[Dict] = []

    for ep in episodes:
        base = {
            "episode_id": ep.id,
            "user_id": ep.user_id,
            "scenario_type": ep.scenario_type.value,
            "topic": ep.topic,
            "location": ep.location,
            "pre_anxiety": ep.pre_anxiety,
            "pre_crying_risk": ep.pre_crying_risk,
            "pre_speech_block_risk": ep.pre_speech_block_risk,
            "crying_level": ep.outcome.crying_level,
            "stress_after": ep.outcome.stress_after,
            "expression_score": ep.outcome.expression_score,
            "relationship_impact": ep.outcome.relationship_impact,
        }
        intensity = {f"prep_{key}_intensity": 0 for key in TREATMENTS}
        for prep in ep.preparations:
            if prep.template_key in TREATMENTS:
                chosen = prep.actual_intensity if prep.actual_intensity is not None else prep.planned_intensity
                intensity[f"prep_{prep.template_key}_intensity"] = chosen or 0
        rows.append({**base, **intensity})

    return pd.DataFrame(rows)


def dml_ate(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    confounder_cols: List[str],
) -> Dict[str, float]:
    """
    Simplified DML estimator:
    1. Predict Y ~ X using RandomForest
    2. Predict binary treatment ~ X using Linear Regression
    3. Regress residualised y on residualised t
    """
    data = df.dropna(subset=[treatment_col, outcome_col] + confounder_cols)
    if len(data) < 30:
        return {"ate": 0.0, "se": math.inf, "n_treated": 0, "n_control": 0}

    T = data[treatment_col].values.astype(float)
    Y = data[outcome_col].values.astype(float)
    X = pd.get_dummies(
        data[confounder_cols],
        columns=["scenario_type", "location", "topic"],
        drop_first=True,
    )
    T_bin = (T >= 3).astype(float)

    y_model = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_leaf=10, n_jobs=-1)
    y_model.fit(X, Y)
    res_y = Y - y_model.predict(X)

    t_model = LinearRegression()
    t_model.fit(X, T_bin)
    res_t = T_bin - t_model.predict(X)

    lr = LinearRegression()
    lr.fit(res_t.reshape(-1, 1), res_y)
    ate = float(lr.coef_[0])
    y_pred = lr.predict(res_t.reshape(-1, 1))
    resid = res_y - y_pred
    sigma2 = np.mean(resid ** 2)
    se = float(math.sqrt(sigma2 / np.sum((res_t - res_t.mean()) ** 2)))
    n_treated = int(T_bin.sum())
    n_control = int((1 - T_bin).sum())

    return {
        "ate": ate,
        "se": se,
        "n_treated": n_treated,
        "n_control": n_control,
    }


def estimate_and_persist_effects() -> None:
    """Main entrypoint for the batch job."""
    with session_scope() as db:
        df = load_episode_dataframe(db)
        if df.empty:
            return

        for user_id, df_user in df.groupby("user_id"):
            for t_key in TREATMENTS:
                t_col = f"prep_{t_key}_intensity"
                for outcome in OUTCOMES:
                    stats = dml_ate(
                        df_user,
                        treatment_col=t_col,
                        outcome_col=outcome,
                        confounder_cols=[
                            "pre_anxiety",
                            "pre_crying_risk",
                            "pre_speech_block_risk",
                            "scenario_type",
                            "location",
                            "topic",
                        ],
                    )
                    if math.isinf(stats["se"]) or stats["n_treated"] == 0 or stats["n_control"] == 0:
                        continue
                    z = 1.96
                    ci_lower = stats["ate"] - z * stats["se"]
                    ci_upper = stats["ate"] + z * stats["se"]

                    effect = (
                        db.query(models.EmotionTreatmentEffect)
                            .filter_by(user_id=user_id, treatment_key=t_key, outcome_name=outcome)
                            .one_or_none()
                    )
                    if effect is None:
                        effect = models.EmotionTreatmentEffect(
                            user_id=user_id,
                            treatment_key=t_key,
                            outcome_name=outcome,
                        )
                        db.add(effect)

                    effect.ate = stats["ate"]
                    effect.ci_lower = ci_lower
                    effect.ci_upper = ci_upper
                    effect.n_treated = stats["n_treated"]
                    effect.n_control = stats["n_control"]
                    effect.model_version = MODEL_VERSION


if __name__ == "__main__":
    estimate_and_persist_effects()

