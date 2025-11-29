"""
Estimate evaluation->crying path coefficients per user.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict

import pandas as pd
from sklearn.linear_model import LinearRegression

from cqox.db import session_scope
from cqox.emotion import models

MIN_EPISODES = 10


def build_user_dataframe(session) -> pd.DataFrame:
    query = (
        session.query(models.EmotionEpisode, models.EmotionOutcome, models.EmotionTraitProfile)
        .join(models.EmotionOutcome, models.EmotionEpisode.id == models.EmotionOutcome.episode_id)
        .outerjoin(
            models.EmotionTraitProfile,
            models.EmotionTraitProfile.user_id == models.EmotionEpisode.user_id,
        )
    )
    rows: list[Dict] = []
    for ep, outcome, trait in query:
        if ep.eval_threat_level is None or ep.suppress_intent_level is None:
            continue
        rows.append(
            {
                "user_id": ep.user_id,
                "E": ep.eval_threat_level,
                "S": ep.pre_anxiety,
                "R": ep.suppress_intent_level,
                "C": outcome.crying_level,
                "A_sa": trait.trait_social_anxiety if trait else None,
                "A_cp": trait.trait_crying_proneness if trait else None,
            }
        )
    return pd.DataFrame(rows)


def estimate_for_user(df_u: pd.DataFrame):
    df_u = df_u.dropna(subset=["E", "S", "R", "C"])
    if len(df_u) < MIN_EPISODES:
        return None

    X_s = df_u[["E", "A_sa"]].fillna(df_u[["E", "A_sa"]].mean(numeric_only=True))
    y_s = df_u["S"].values
    lr_s = LinearRegression().fit(X_s, y_s)
    alpha_eval = float(lr_s.coef_[0])

    X_c = df_u[["E", "S", "R", "A_cp"]].fillna(df_u[["E", "S", "R", "A_cp"]].mean(numeric_only=True))
    y_c = df_u["C"].values
    lr_c = LinearRegression().fit(X_c, y_c)
    beta_eval = float(lr_c.coef_[0])
    beta_stress = float(lr_c.coef_[1])
    beta_suppress = float(lr_c.coef_[2])

    indirect = alpha_eval * beta_stress
    total = beta_eval + indirect

    return {
        "alpha_eval_to_stress": alpha_eval,
        "beta_eval_to_cry": beta_eval,
        "beta_stress_to_cry": beta_stress,
        "beta_suppress_to_cry": beta_suppress,
        "indirect_eval_to_cry": indirect,
        "total_eval_to_cry": total,
        "n_episodes": len(df_u),
    }


def estimate_and_persist_paths() -> None:
    with session_scope() as session:
        df = build_user_dataframe(session)
        if df.empty:
            return
        for user_id, df_user in df.groupby("user_id"):
            stats = estimate_for_user(df_user)
            if not stats:
                continue
            summary = (
                session.query(models.EmotionPathSummary).filter_by(user_id=user_id).one_or_none()
            )
            if summary is None:
                summary = models.EmotionPathSummary(user_id=user_id)
                session.add(summary)
            for key, value in stats.items():
                setattr(summary, key, value)
            summary.updated_at = datetime.utcnow()


if __name__ == "__main__":
    estimate_and_persist_paths()
