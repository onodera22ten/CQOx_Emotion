"""
Analytics Engine for Emotion CQOx
Implements Δ Stress, Δ Expression calculations with confidence intervals
"""
from typing import List, Tuple, Optional
import math
from dataclasses import dataclass
from enum import Enum

from .schemas import ScenarioType


@dataclass
class DeltaMetric:
    mean: float
    ci95: Tuple[float, float]


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PreparationEffectiveness:
    template_key: str
    scenario_type: ScenarioType
    n_with: int
    n_without: int
    delta_stress: DeltaMetric
    delta_expression: DeltaMetric
    confidence_label: ConfidenceLevel


@dataclass
class EpisodeData:
    """Single episode data for analysis"""
    pre_anxiety: int
    stress_after: Optional[int]
    expression_score: Optional[int]
    preparations: dict[str, int]  # template_key -> intensity


class AnalyticsEngine:
    """
    Causal analytics engine for Emotion CQOx

    Implements within-subject comparison and simple regression
    to estimate preparation effectiveness
    """

    def __init__(self):
        pass

    def calculate_delta_stress(
        self,
        episodes: List[EpisodeData]
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate ΔStress = pre_anxiety - stress_after

        Returns:
            (mean, (ci_low, ci_high))
        """
        deltas = []
        for ep in episodes:
            if ep.stress_after is not None:
                delta = ep.pre_anxiety - ep.stress_after
                deltas.append(delta)

        if not deltas:
            return (0.0, (0.0, 0.0))

        mean = sum(deltas) / len(deltas)
        std = math.sqrt(sum((x - mean) ** 2 for x in deltas) / max(len(deltas) - 1, 1))

        # 95% CI using t-distribution approximation
        # For simplicity, using z=1.96 (accurate for n>30)
        margin = 1.96 * std / math.sqrt(len(deltas))

        return (mean, (mean - margin, mean + margin))

    def calculate_delta_expression(
        self,
        episodes: List[EpisodeData]
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate mean expression_score with CI
        """
        scores = [ep.expression_score for ep in episodes if ep.expression_score is not None]

        if not scores:
            return (0.0, (0.0, 0.0))

        mean = sum(scores) / len(scores)
        std = math.sqrt(sum((x - mean) ** 2 for x in scores) / max(len(scores) - 1, 1))

        margin = 1.96 * std / math.sqrt(len(scores))

        return (mean, (mean - margin, mean + margin))

    def analyze_preparation_effect(
        self,
        template_key: str,
        scenario_type: ScenarioType,
        all_episodes: List[EpisodeData]
    ) -> Optional[PreparationEffectiveness]:
        """
        Analyze the effect of a specific preparation template

        Compares episodes WITH this preparation vs WITHOUT
        """
        # Filter by scenario_type (for more accurate comparison)
        # In real implementation, you'd load this filtering from DB

        with_prep = []
        without_prep = []

        for ep in all_episodes:
            if template_key in ep.preparations and ep.preparations[template_key] > 0:
                with_prep.append(ep)
            else:
                without_prep.append(ep)

        if len(with_prep) < 2 or len(without_prep) < 2:
            # Not enough data
            return None

        # Calculate ΔStress for each group
        delta_stress_with = self.calculate_delta_stress(with_prep)
        delta_stress_without = self.calculate_delta_stress(without_prep)

        # Effect = difference between groups
        delta_stress_effect = delta_stress_with[0] - delta_stress_without[0]
        delta_stress_ci = (
            delta_stress_with[1][0] - delta_stress_without[1][1],
            delta_stress_with[1][1] - delta_stress_without[1][0],
        )

        # Calculate ΔExpression for each group
        delta_expr_with = self.calculate_delta_expression(with_prep)
        delta_expr_without = self.calculate_delta_expression(without_prep)

        delta_expr_effect = delta_expr_with[0] - delta_expr_without[0]
        delta_expr_ci = (
            delta_expr_with[1][0] - delta_expr_without[1][1],
            delta_expr_with[1][1] - delta_expr_without[1][0],
        )

        # Confidence label
        confidence = self._determine_confidence(len(with_prep), len(without_prep))

        return PreparationEffectiveness(
            template_key=template_key,
            scenario_type=scenario_type,
            n_with=len(with_prep),
            n_without=len(without_prep),
            delta_stress=DeltaMetric(
                mean=delta_stress_effect,
                ci95=[delta_stress_ci[0], delta_stress_ci[1]]
            ),
            delta_expression=DeltaMetric(
                mean=delta_expr_effect,
                ci95=[delta_expr_ci[0], delta_expr_ci[1]]
            ),
            confidence_label=confidence
        )

    def _determine_confidence(self, n_with: int, n_without: int) -> ConfidenceLevel:
        """Determine confidence level based on sample sizes"""
        min_n = min(n_with, n_without)

        if min_n >= 30:
            return ConfidenceLevel.HIGH
        elif min_n >= 10:
            return ConfidenceLevel.MEDIUM
        elif min_n >= 2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.LOW

    def predict_outcome(
        self,
        pre_anxiety: int,
        pre_crying_risk: int,
        pre_speech_block_risk: int,
        preparations: dict[str, int]
    ) -> dict:
        """
        Predict outcomes based on preparation plan

        Uses the same generative model as the CSV generator
        for consistency
        """
        # Calculate total prep effect
        total_prep_effect = (
            0.25 * preparations.get("journaling_10m", 0)
            + 0.35 * preparations.get("three_messages", 0)
            + 0.20 * preparations.get("breathing_4_7_8", 0)
            + 0.25 * preparations.get("roleplay_self_qa", 0)
        ) / 10.0

        # Predict stress_after
        stress_after_mean = max(pre_anxiety - 1.0 - 1.5 * total_prep_effect, 0)
        stress_after_std = 2.0

        # Predict crying_level
        crying_base = (
            pre_crying_risk
            - 0.3 * preparations.get("journaling_10m", 0) / 2
            - 0.2 * preparations.get("breathing_4_7_8", 0) / 2
        )
        crying_mean = max(min(crying_base, 10), 0)
        crying_std = 2.0

        # Predict expression_score
        # Assume speech_block and stress_during for calculation
        speech_block_est = pre_speech_block_risk - 0.3 * preparations.get("three_messages", 0) / 2
        speech_block_est = max(min(speech_block_est, 10), 0)

        expr_base = (
            5.0
            + 0.4 * preparations.get("three_messages", 0) / 2
            + 0.3 * preparations.get("roleplay_self_qa", 0) / 2
            - 0.25 * speech_block_est
            - 0.15 * crying_mean
        )
        expr_mean = max(min(expr_base, 10), 0)
        expr_std = 2.5

        # Predict relationship_impact
        rel_base = (
            -1
            + 0.4 * (expr_mean - 5) / 2
        )
        rel_mean = max(min(rel_base, 5), -5)
        rel_std = 1.8

        return {
            "stress_after": {
                "mean": stress_after_mean,
                "ci95": [
                    max(stress_after_mean - 1.96 * stress_after_std, 0),
                    min(stress_after_mean + 1.96 * stress_after_std, 10)
                ]
            },
            "crying_level": {
                "mean": crying_mean,
                "ci95": [
                    max(crying_mean - 1.96 * crying_std, 0),
                    min(crying_mean + 1.96 * crying_std, 10)
                ]
            },
            "expression_score": {
                "mean": expr_mean,
                "ci95": [
                    max(expr_mean - 1.96 * expr_std, 0),
                    min(expr_mean + 1.96 * expr_std, 10)
                ]
            },
            "relationship_impact": {
                "mean": rel_mean,
                "ci95": [
                    max(rel_mean - 1.96 * rel_std, -5),
                    min(rel_mean + 1.96 * rel_std, 5)
                ]
            }
        }

    def calculate_total_reward(
        self,
        predicted_stress_after: float,
        predicted_expression: float,
        predicted_relationship: float,
        pre_anxiety: float,
        weight_relief: float,
        weight_expression: float,
        weight_relationship: float
    ) -> float:
        """
        Calculate total reward based on user preference weights

        This is the key function that connects slider Layer B (preferences)
        to the recommendation/bandit algorithm
        """
        # Relief (楽さ) = reduction in stress
        relief_reward = pre_anxiety - predicted_stress_after

        # Expression (伝達度) = how well expressed (0-10)
        expression_reward = predicted_expression

        # Relationship (関係維持) = relationship impact (-5 to +5)
        relationship_reward = predicted_relationship

        # Normalize and scale
        relief_normalized = relief_reward / 10.0  # max possible delta is 10
        expression_normalized = expression_reward / 10.0
        relationship_normalized = (predicted_relationship + 5) / 10.0  # map -5~+5 to 0~1

        # Weighted sum
        total = (
            weight_relief * relief_normalized
            + weight_expression * expression_normalized
            + weight_relationship * relationship_normalized
        )

        return total
