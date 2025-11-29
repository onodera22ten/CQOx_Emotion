#!/usr/bin/env python3
"""
Emotion CQOx サンプル CSV 生成スクリプト

1行 = 1エピソード (Episode)
各行には:
- 事前状態 (pre_anxiety / pre_crying_risk / pre_speech_block_risk)
- 準備の強度 (prep_*_intensity)
- 当日のアウトカム (stress, crying, expression, relationship)
- 振り返り (reflection)
が入る。生成ロジックは仕様書の 2.章に対応。
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed. Run: pip install pandas")
    exit(1)


def clipped_normal(mu: float, sigma: float, low: float, high: float) -> float:
    """正規分布を low〜high の範囲にクリップして返す。"""
    x = random.gauss(mu, sigma)
    return max(low, min(high, x))


def generate_rows(n_rows: int, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    today = datetime(2025, 11, 28)

    scenario_types = [
        "interview",
        "one_on_one",
        "partner",
        "family",
        "friend",
        "client",
        "other",
    ]
    scenario_weights = [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10]

    topics_by_type = {
        "interview": ["転職理由", "キャリアの方向性", "過去の退職理由", "評価面談"],
        "one_on_one": ["評価フィードバック", "キャリア相談", "業務負荷の相談", "人間関係の摩擦"],
        "partner": ["将来の暮らし", "お金の話", "結婚について", "別れ話", "距離を置きたい"],
        "family": ["親への近況報告", "進路の話", "介護の相談", "家族との距離感"],
        "friend": ["久しぶりの再会", "価値観のズレ", "謝罪", "疎遠になっている理由"],
        "client": ["トラブルの謝罪", "値上げ交渉", "契約更新", "納期遅延の相談"],
        "other": ["自己開示の練習", "セラピーではない雑談", "将来への漠然とした不安"],
    }

    locations = ["online", "office", "home", "cafe", "coworking", "client_site", "park"]

    partner_reactions = [
        "very_positive",
        "positive",
        "neutral",
        "negative",
        "very_negative",
        "unknown",
    ]

    reflection_templates = [
        "少し泣いたけど言いたいことは伝えられた。",
        "ほとんど話せずに終わってしまった。次は準備を変えたい。",
        "かなり落ち着いて話せた。準備が効いた感じがある。",
        "相手の反応が予想外で混乱した。振り返りが必要。",
        "泣かなかったが本音をあまり出せなかった。",
        "かなりつらかったが、終わってみると少し楽になった。",
        "正直、今回はタイミングを間違えたかもしれない。",
    ]

    base_anxiety_by_type = {
        "interview": 7.5,
        "one_on_one": 6.0,
        "partner": 7.0,
        "family": 5.5,
        "friend": 4.5,
        "client": 6.5,
        "other": 5.0,
    }

    rows: list[dict] = []

    for episode_id in range(1, n_rows + 1):
        # --- user & scenario ---
        # ヘビーユーザー (1〜5) に重みを付ける
        user_id = random.choices(
            population=list(range(1, 31)),
            weights=[5] * 5 + [1] * 25,
            k=1,
        )[0]

        scenario_type = random.choices(
            population=scenario_types,
            weights=scenario_weights,
            k=1,
        )[0]

        topic = random.choice(topics_by_type[scenario_type])

        # --- scheduled_at ---
        days_offset = random.randint(-730, 90)  # 過去2年〜未来3か月
        time_offset = timedelta(
            days=days_offset,
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59),
        )
        scheduled_at = today + time_offset
        location = random.choice(locations)

        # --- status ---
        if scheduled_at > today:
            status = random.choices(["planned", "cancelled"], weights=[0.8, 0.2], k=1)[0]
        else:
            status = random.choices(
                ["completed", "cancelled"], weights=[0.85, 0.15], k=1
            )[0]

        # --- pre state ---
        base_anxiety = base_anxiety_by_type[scenario_type]
        pre_anxiety = int(round(clipped_normal(base_anxiety, 2.0, 0, 10)))

        crying_topic_bonus = 1 if topic in ["過去の退職理由", "別れ話", "距離を置きたい", "介護の相談"] else 0
        pre_crying_risk = int(
            round(
                clipped_normal(base_anxiety - 1 + crying_topic_bonus, 2.0, 0, 10)
            )
        )

        pre_speech_block_risk = int(
            round(clipped_normal(base_anxiety - 0.5, 2.0, 0, 10))
        )

        # --- preparations ---
        def prep_prob(key: str) -> float:
            if key == "journaling_10m":
                return 0.55 if scenario_type in ["interview", "partner", "family"] else 0.35
            if key == "three_messages":
                return 0.65 if scenario_type in ["interview", "client", "one_on_one"] else 0.40
            if key == "breathing_4_7_8":
                return 0.50
            if key == "roleplay_self_qa":
                return 0.40 if scenario_type in ["interview", "client"] else 0.25
            if key == "safe_word_plan":
                return 0.25 if scenario_type in ["partner", "family", "friend"] else 0.10
            return 0.0

        prep_keys = [
            "journaling_10m",
            "three_messages",
            "breathing_4_7_8",
            "roleplay_self_qa",
            "safe_word_plan",
        ]

        prep_intensities: dict[str, int] = {}
        for key in prep_keys:
            if random.random() < prep_prob(key):
                # しっかり実施したケース (3〜10)
                intensity = int(round(clipped_normal(7, 2, 3, 10)))
            else:
                # やろうとして少しだけやったケース (1〜3) を 5% 混ぜる
                if random.random() < 0.05:
                    intensity = random.randint(1, 3)
                else:
                    intensity = 0
            prep_intensities[key] = intensity

        # --- outcomes (completed only) ---
        if status == "completed":
            total_prep_effect = (
                0.25 * prep_intensities["journaling_10m"]
                + 0.35 * prep_intensities["three_messages"]
                + 0.20 * prep_intensities["breathing_4_7_8"]
                + 0.25 * prep_intensities["roleplay_self_qa"]
            ) / 10.0

            stress_during = int(
                round(
                    clipped_normal(
                        pre_anxiety + 0.5 - 0.3 * total_prep_effect,
                        1.8,
                        0,
                        10,
                    )
                )
            )

            stress_after = int(
                round(
                    clipped_normal(
                        max(pre_anxiety - 1.0 - 1.5 * total_prep_effect, 0),
                        2.0,
                        0,
                        10,
                    )
                )
            )

            crying_base = (
                pre_crying_risk
                + 0.5 * (stress_during - pre_anxiety)
                - 0.3 * prep_intensities["journaling_10m"] / 2
                - 0.2 * prep_intensities["breathing_4_7_8"] / 2
            )
            crying_level = int(round(clipped_normal(crying_base, 2.0, 0, 10)))

            speech_block_base = (
                pre_speech_block_risk
                + 0.4 * (stress_during - pre_anxiety)
                - 0.3 * prep_intensities["three_messages"] / 2
            )
            speech_block_level = int(
                round(clipped_normal(speech_block_base, 2.0, 0, 10))
            )

            expr_base = (
                5.0
                + 0.4 * prep_intensities["three_messages"] / 2
                + 0.3 * prep_intensities["roleplay_self_qa"] / 2
                - 0.25 * speech_block_level
                - 0.15 * crying_level
            )
            expression_score = int(
                round(clipped_normal(expr_base, 2.5, 0, 10))
            )

            rel_base = (
                -1
                + 0.4 * (expression_score - 5) / 2
                - 0.25 * max(stress_during - 6, 0)
            )
            relationship_impact = int(
                round(clipped_normal(rel_base, 1.8, -5, 5))
            )

            partner_reaction = random.choices(
                population=partner_reactions,
                weights=[
                    max(0.1, 0.3 + 0.05 * relationship_impact),  # very_positive
                    max(0.1, 0.3 + 0.04 * relationship_impact),  # positive
                    0.3,  # neutral
                    max(0.05, 0.2 - 0.04 * relationship_impact),  # negative
                    max(0.02, 0.1 - 0.05 * relationship_impact),  # very_negative
                    0.2,  # unknown
                ],
                k=1,
            )[0]

            if random.random() < 0.7:
                days_after = random.randint(1, 14)
                would_repeat = int(
                    round(
                        clipped_normal(
                            max(
                                5,
                                expression_score
                                - max(crying_level - 4, 0),
                            ),
                            2.0,
                            0,
                            10,
                        )
                    )
                )
                reflection_short = random.choice(reflection_templates)
            else:
                days_after = ""
                would_repeat = ""
                reflection_short = ""

        else:
            # planned / cancelled の場合はアウトカム列を欠損扱いにする
            stress_during = ""
            stress_after = ""
            crying_level = ""
            speech_block_level = ""
            expression_score = ""
            relationship_impact = ""
            partner_reaction = ""
            days_after = ""
            would_repeat = ""
            reflection_short = ""

        # 0 は CSV 上では "" にして「未実施・欠損」として扱う
        def intensity_or_empty(key: str) -> str | int:
            return prep_intensities[key] if prep_intensities[key] > 0 else ""

        row = {
            "episode_id": episode_id,
            "user_id": user_id,
            "status": status,
            "scenario_type": scenario_type,
            "topic": topic,
            "scheduled_at": scheduled_at.isoformat(),
            "location": location,
            "pre_anxiety": pre_anxiety,
            "pre_crying_risk": pre_crying_risk,
            "pre_speech_block_risk": pre_speech_block_risk,
            "prep_journaling_10m_intensity": intensity_or_empty("journaling_10m"),
            "prep_three_messages_intensity": intensity_or_empty("three_messages"),
            "prep_breathing_4_7_8_intensity": intensity_or_empty("breathing_4_7_8"),
            "prep_roleplay_self_qa_intensity": intensity_or_empty("roleplay_self_qa"),
            "prep_safe_word_plan_intensity": intensity_or_empty("safe_word_plan"),
            "stress_during": stress_during,
            "stress_after": stress_after,
            "crying_level": crying_level,
            "speech_block_level": speech_block_level,
            "expression_score": expression_score,
            "relationship_impact": relationship_impact,
            "partner_reaction": partner_reaction,
            "days_after_reflection": days_after,
            "would_repeat_preparation": would_repeat,
            "reflection_short": reflection_short,
        }

        rows.append(row)

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Emotion CQOx sample CSV with pseudo-causal structure"
    )
    parser.add_argument(
        "--n-rows", type=int, default=5000, help="生成する行数 (default: 5000)"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="乱数シード (default: 42)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="emotion_cqox_sample_5000.csv",
        help="出力 CSV パス",
    )
    args = parser.parse_args()

    print(f"Generating {args.n_rows} rows with seed={args.seed}...")
    df = generate_rows(args.n_rows, seed=args.seed)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(args.output, index=False, encoding='utf-8')
    print(f"✓ Wrote: {args.output}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Status distribution:")
    print(df['status'].value_counts().to_dict())


if __name__ == "__main__":
    main()
