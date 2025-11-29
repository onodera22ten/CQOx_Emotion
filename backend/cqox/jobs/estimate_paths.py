"""
Estimate evaluation -> crying path coefficients with ridge regression and bootstrap.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from cqox.db import session_scope
from cqox.emotion import models

MIN_EPISODES = 10
BOOTSTRAP_SAMPLES = 100


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
                "partner_role": ep.context_partner_role or "未設定",
                "E": ep.eval_threat_level,
                "S": ep.pre_anxiety,
                "R": ep.suppress_intent_level,
                "C": outcome.crying_level,
                "A_sa": trait.trait_social_anxiety if trait else None,
                "A_cp": trait.trait_crying_proneness if trait else None,
            }
        )
    return pd.DataFrame(rows)


def _fit_ridge_coeffs(X: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray]:
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds[stds == 0] = 1.0
    X_scaled = (X - means) / stds
    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)
    coef_scaled = model.coef_
    intercept = model.intercept_ - float(np.sum(coef_scaled * means / stds))
    coef = coef_scaled / stds
    return intercept, coef


def _bootstrap_stats(
    X: np.ndarray, y: np.ndarray, feature_names: list[str]
) -> Dict[str, Tuple[float, float, float]]:
    intercepts = []
    coefs = []
    for _ in range(BOOTSTRAP_SAMPLES):
        idx = np.random.choice(len(y), size=len(y), replace=True)
        inter, coef = _fit_ridge_coeffs(X[idx], y[idx])
        intercepts.append(inter)
        coefs.append(coef)
    intercepts = np.array(intercepts)
    coefs = np.array(coefs)

    def summarize(series: np.ndarray):
        return series.mean(), np.percentile(series, 2.5), np.percentile(series, 97.5)

    stats = {"intercept": summarize(intercepts)}
    for i, name in enumerate(feature_names):
        stats[name] = summarize(coefs[:, i])
    return stats


def estimate_for_user(df_u: pd.DataFrame):
    df_u = df_u.dropna(subset=["E", "S", "R", "C"])
    if len(df_u) < MIN_EPISODES:
        return None

    X_s = df_u[["E", "A_sa"]].fillna(df_u[["E", "A_sa"]].mean(numeric_only=True)).values
    y_s = df_u["S"].values
    (_, _), stats_s = _fit_and_bootstrap(X_s, y_s, ["E", "A_sa"])
    alpha_eval = stats_s["E"][0]

    X_c = df_u[["E", "S", "R", "A_cp"]].fillna(df_u[["E", "S", "R", "A_cp"]].mean(numeric_only=True)).values
    y_c = df_u["C"].values
    intercept, coef = _fit_ridge_coeffs(X_c, y_c)
    boot_stats = _bootstrap_stats(X_c, y_c, ["E", "S", "R", "A_cp"])

    beta_eval = boot_stats["E"][0]
    beta_stress = boot_stats["S"][0]
    beta_suppress = boot_stats["R"][0]
    beta_trait = boot_stats["A_cp"][0]
    indirect = alpha_eval * beta_stress
    total = beta_eval + indirect

    return {
        "intercept": intercept,
        "intercept_lo": boot_stats["intercept"][1],
        "intercept_hi": boot_stats["intercept"][2],
        "alpha_eval_to_stress": alpha_eval,
        "alpha_eval_to_stress_lo": stats_s["E"][1],
        "alpha_eval_to_stress_hi": stats_s["E"][2],
        "beta_eval_to_cry": beta_eval,
        "beta_eval_to_cry_lo": boot_stats["E"][1],
        "beta_eval_to_cry_hi": boot_stats["E"][2],
        "beta_stress_to_cry": beta_stress,
        "beta_stress_to_cry_lo": boot_stats["S"][1],
        "beta_stress_to_cry_hi": boot_stats["S"][2],
        "beta_suppress_to_cry": beta_suppress,
        "beta_suppress_to_cry_lo": boot_stats["R"][1],
        "beta_suppress_to_cry_hi": boot_stats["R"][2],
        "beta_trait_to_cry": beta_trait,
        "beta_trait_to_cry_lo": boot_stats["A_cp"][1],
        "beta_trait_to_cry_hi": boot_stats["A_cp"][2],
        "indirect_eval_to_cry": indirect,
        "indirect_eval_to_cry_lo": (stats_s["E"][1] * boot_stats["S"][1]),
        "indirect_eval_to_cry_hi": (stats_s["E"][2] * boot_stats["S"][2]),
        "total_eval_to_cry": total,
        "total_eval_to_cry_lo": boot_stats["E"][1] + (stats_s["E"][1] * boot_stats["S"][1]),
        "total_eval_to_cry_hi": boot_stats["E"][2] + (stats_s["E"][2] * boot_stats["S"][2]),
        "n_episodes": len(df_u),
    }


def _fit_and_bootstrap(X, y, feature_names):
    inter, coef = _fit_ridge_coeffs(X, y)
    stats = _bootstrap_stats(X, y, feature_names)
    return (inter, coef), stats


def update_partner_summary(session, user_id: int, df_u: pd.DataFrame):
    for partner_role, df_partner in df_u.groupby("partner_role"):
        if len(df_partner) < MIN_EPISODES:
            continue
        stats = estimate_for_user(df_partner)
        if not stats:
            continue
        record = (
            session.query(models.EmotionPathPartnerSummary)
            .filter_by(user_id=user_id, partner_role=partner_role)
            .one_or_none()
        )
        if record is None:
            record = models.EmotionPathPartnerSummary(
                user_id=user_id,
                partner_role=partner_role,
            )
            session.add(record)
        record.total_eval_to_cry = stats["total_eval_to_cry"]
        record.n_episodes = stats["n_episodes"]
        record.updated_at = datetime.utcnow()


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
            update_partner_summary(session, user_id, df_user)


if __name__ == "__main__":
    estimate_and_persist_paths()
