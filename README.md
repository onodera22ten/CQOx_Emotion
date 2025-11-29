# Emotion CQOx - Emotional Episode Optimizer

**一言で言うと**: Google / Netflix / Meta / BCG / WPP のトップチームが内製している"因果ベースの意思決定コンソール"を、一般企業でも使える形に落とし込んだもの + 感情・メンタルヘルス領域への特化

> 「面接・1on1・大事な話し合い」などの感情負荷の高いエピソードごとに、事前準備と結果をログし、本人にとって"楽で、ちゃんと伝えられる"準備パターンを見つけるための非医療・非診断の意思決定支援プラットフォーム

---

## 📊 What is Emotion CQOx?

Emotion CQOxは、**エピソード(Episode) ベースの因果推論プラットフォーム**です。

### 中核概念

```
Episode = 1回の出来事 (面接・1on1・話し合い etc.)
  ├── Preparation: 事前準備 (ジャーナリング・呼吸法・ロールプレイ etc.)
  ├── Outcome: 当日の結果 (ストレス・涙・伝達度・関係への影響)
  └── Reflection: 後日の振り返り
```

**目的**:
- 「自分の想いを話そうとすると涙が出る / 固まる」人が
- どんな条件・話題・準備でそうなりやすいかを可視化し
- 「自分に合う準備・言い方・ペース配分」をデータベース化する

### What Makes It Different?

1. **非医療・非診断**
   診断や治療は一切行わない。あくまで「自分の実験ログ」として使う。

2. **因果の言語で説明**
   マーケティング CQOx と同じ「ΔStress」「ΔExpression」「CAS (Causal Assurance Score)」で準備効果を提示。

3. **多目的最適化**
   「涙をゼロにする」ではなく、「楽さ × 伝達度 × 関係性」のバランスを本人が決める。

4. **スライダーUI**
   - Layer A: Episode直前の状態 (しんどさ・泣きそう度・詰まりそう度)
   - Layer B: 本人の目的関数 (楽さ重視 vs 伝えたい vs 関係維持)
   - Layer C: What-if シミュレーション (準備プランの予測)

---

## 🚀 Quick Start

### 1. サンプルデータ生成

```bash
# 依存関係インストール
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pandas numpy scipy

# 5000行のサンプルCSV生成
python scripts/generate_emotion_cqox_sample.py \
  --n-rows 5000 \
  --seed 42 \
  --output sample/emotion_cqox_sample_5000.csv
```

生成されるCSV:
- **5000行** = 5000エピソード
- **25列** = 事前状態・準備・アウトカム・振り返り
- **擬似因果構造** = 準備 → ストレス軽減 / 表現向上の関係が埋め込まれている
- **現実的な欠損** = cancelled/planned は outcome が空、70%だけ reflection あり

### 2. バックエンド起動

```bash
cd backend
pip install -r requirements.txt

# PostgreSQL を起動 (Docker推奨)
docker run -d \
  --name emotion-cqox-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=emotion_cqox \
  -p 5432:5432 \
  postgres:15

# マイグレーション
alembic upgrade head

# FastAPI サーバー起動
uvicorn cqox.main:app --reload --host 0.0.0.0 --port 8000
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### 3. フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

---

## 📁 Project Structure

```
CQOx_Emotion/
├── backend/
│   ├── cqox/
│   │   ├── emotion/
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   ├── schemas.py         # Pydantic schemas (3-layer sliders)
│   │   │   ├── analytics.py       # Δ Calculations & Bandit
│   │   │   ├── safety.py          # High-risk text detection
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   └── emotion.py         # FastAPI endpoints
│   │   └── main.py
│   ├── alembic/                   # DB migrations
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── features/emotion/
│   │   │   ├── components/
│   │   │   │   ├── EpisodeQuickSliders.tsx        # Layer A
│   │   │   │   ├── PreferenceSliders.tsx          # Layer B
│   │   │   │   ├── PreparationSimulator.tsx       # Layer C
│   │   │   │   ├── CausalEffectForestChart.tsx    # ATE 可視化
│   │   │   │   └── EmotionTimelineChart.tsx       # 時系列可視化
│   │   │   └── pages/emotion/
│   │   │       ├── EmotionEpisodeCreatePage.tsx
│   │   │       ├── EmotionOutcomeLogPage.tsx
│   │   │       └── EmotionDashboardPage.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── README.md
│
├── scripts/
│   └── generate_emotion_cqox_sample.py   # CSV generator
│
├── sample/
│   └── emotion_cqox_sample_5000.csv      # Generated data
│
├── docs/
│   ├── SPEC.md                   # Full specification (from PDF)
│   └── API.md                    # API documentation
│
└── README.md                     # This file
```

---

## 🔧 Core Features

### 1. Episode Management

**エピソード登録**: 面接・1on1・話し合いを事前/事後に記録

```typescript
// 状態スライダー (Layer A)
<EpisodeQuickSliders
  preAnxiety={7}           // 0-10
  preCryingRisk={6}        // 0-10
  preSpeechBlockRisk={8}   // 0-10
  onChange={setPre}
/>
```

### 2. Preparation Templates

5つの準備パターン:
- `journaling_10m`: 10分の書き出し (ジャーナリング)
- `three_messages`: 伝えたいメッセージを3つ決める
- `breathing_4_7_8`: 4-7-8呼吸法
- `roleplay_self_qa`: 自分でQ&Aロールプレイ
- `safe_word_plan`: セーフワード (つらくなった時の合図) を決める

### 3. Analytics Engine

**ΔStress**: `pre_anxiety - stress_after`
**ΔExpression**: `expression_score` の変化

```python
from cqox.emotion.analytics import AnalyticsEngine

engine = AnalyticsEngine()
effect = engine.analyze_preparation_effect(
    template_key="journaling_10m",
    scenario_type="interview",
    all_episodes=episodes
)

print(f"ΔStress: {effect.delta_stress.mean} ({effect.delta_stress.ci95})")
print(f"ΔExpression: {effect.delta_expression.mean}")
print(f"Confidence: {effect.confidence_label}")
```

### 4. Preference Profile (Slider Layer B)

**目的関数を本人が決める**:

```typescript
<PreferenceSliders
  relief={5}           // 楽さ重視度 (0-10)
  expression={7}       // 伝えたい度 (0-10)
  relationship={3}     // 関係維持度 (0-10)
  onChange={setPrefs}
/>
```

バックエンドで報酬関数に組み込み:

```python
total_reward = (
    w_relief * relief_reward
    + w_expression * expression_reward
    + w_relationship * relationship_reward
)
```

### 5. What-if Simulation (Slider Layer C)

**準備プランの予測**:

```bash
POST /api/emotion/simulate
{
  "pre_anxiety": 7,
  "prep_journaling_10m": 8,
  "prep_three_messages": 6
}

Response:
{
  "predicted_stress_after": {"mean": 4.2, "ci95": [2.1, 6.3]},
  "predicted_expression_score": {"mean": 6.5, "ci95": [4.0, 9.0]},
  "total_reward": 0.72,
  "disclaimer": "This is a prediction based on your past data..."
}
```

### 6. Safety Guardrails

**ハイリスクテキスト検知**:

```python
from cqox.emotion.safety import SafetyGuard

guard = SafetyGuard()
result = guard.check_text("死にたいと思うことがある")

# result.is_safe = False
# result.risk_level = "critical"
# result.resources = [いのちの電話, こころの健康相談統一ダイヤル, ...]
```

検知されたテキストは:
- **LLMに送信しない**
- ハッシュのみログ保存
- 専門機関リソースを表示
- **利用継続ではなく離脱を促す**

---

## 📊 Sample CSV Structure

| 列名 | 型 | 説明 | 欠損 |
|------|-----|------|------|
| `episode_id` | int | エピソードID (1-5000) | なし |
| `user_id` | int | ユーザーID (1-30, 1-5はヘビーユーザー) | なし |
| `status` | str | completed / planned / cancelled | なし |
| `scenario_type` | str | interview / one_on_one / partner / family / friend / client / other | なし |
| `topic` | str | 「転職理由」「別れ話」など | なし |
| `scheduled_at` | str | ISO8601 (過去2年〜未来3か月) | なし |
| `pre_anxiety` | int | 0-10 | なし |
| `pre_crying_risk` | int | 0-10 | なし |
| `pre_speech_block_risk` | int | 0-10 | なし |
| `prep_journaling_10m_intensity` | int or "" | 0-10, 0は空文字 | あり |
| `prep_three_messages_intensity` | int or "" | 0-10 | あり |
| `prep_breathing_4_7_8_intensity` | int or "" | 0-10 | あり |
| `prep_roleplay_self_qa_intensity` | int or "" | 0-10 | あり |
| `prep_safe_word_plan_intensity` | int or "" | 0-10 | あり |
| `stress_during` | int or "" | 0-10, completed のみ | あり |
| `stress_after` | int or "" | 0-10, completed のみ | あり |
| `crying_level` | int or "" | 0-10 | あり |
| `speech_block_level` | int or "" | 0-10 | あり |
| `expression_score` | int or "" | 0-10 | あり |
| `relationship_impact` | int or "" | -5 to +5 | あり |
| `partner_reaction` | str or "" | very_positive / positive / neutral / negative / very_negative / unknown | あり |
| `days_after_reflection` | int or "" | 1-14 | あり |
| `would_repeat_preparation` | int or "" | 0-10 | あり |
| `reflection_short` | str or "" | 日本語短文 | あり |

**重要**:
- 数値でも「未実施・未記録」は `0` ではなく `""`（空文字）
- `status` によってアウトカム列が系統的に欠損 → MNAR (Missing Not At Random)

---

## 🎯 API Endpoints

### Episodes

```bash
POST   /api/emotion/scenarios              # Create episode
GET    /api/emotion/scenarios              # List episodes
GET    /api/emotion/scenarios/{id}         # Get episode detail
POST   /api/emotion/scenarios/{id}/preparations  # Add preparation
POST   /api/emotion/scenarios/{id}/outcomes     # Record outcome
POST   /api/emotion/scenarios/{id}/reflections  # Add reflection
```

### Analytics

```bash
GET    /api/emotion/dashboard/summary      # Dashboard summary with ΔStress/ΔExpression
```

### Preference Profile

```bash
GET    /api/emotion/preferences/me         # Get my preferences
POST   /api/emotion/preferences/me         # Update preferences
```

### Safety

```bash
POST   /api/emotion/safety/check           # Check text for high-risk content
```

### Simulation

```bash
POST   /api/emotion/simulate               # Predict outcomes for preparation plan
```

### Import/Export

```bash
POST   /api/emotion/import/csv             # Import episodes from CSV
GET    /api/emotion/export/csv             # Export to CSV
```

---

## 🔬 Causal Inference Workflow

```
┌─────────────────┐
│  Episode Log    │
│ (Pre + Prep +   │
│  Outcome +      │
│  Reflection)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Within-Subject  │
│   Comparison    │
│ (with prep vs   │
│  without prep)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ΔStress        │
│  ΔExpression    │
│  + CI (95%)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recommendation  │
│ (Contextual     │
│  Bandit)        │
└─────────────────┘
```

---

## 🛡️ Safety & Ethics

### Boundary Conditions

**やること**:
- 個人レベルの実験ログ・可視化
- 準備パターンの効果推定（因果の言語で）
- ハイリスク検知 → 専門機関への誘導

**やらないこと** (明示的に):
- うつ病・PTSD等の診断・評価
- 医療専門家の判断を代替するスコアリング
- 自殺リスク予測モデルの自動運用
- 「涙をゼロにする」単一目的最適化

### High-Risk Detection

```python
# backend/cqox/emotion/safety.py

class SafetyGuard:
    critical_patterns = [
        r'死にたい',
        r'自殺',
        r'消えたい',
        ...
    ]

    def check_text(self, text: str) -> SafetyCheckResponse:
        # Detect patterns
        # Provide resources
        # Log (hash only, NOT the text itself)
        pass
```

**ハイリスク検知時の動作**:
1. LLMへの送信禁止
2. 専門窓口リソース表示 (いのちの電話・厚労省SNS相談等)
3. **利用継続ではなく離脱を促す**

---

## 🌐 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  User Interface (React)                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │ Episode Quick  │  │  Preference    │  │ Simulation │ │
│  │   Sliders      │  │   Sliders      │  │   Panel    │ │
│  │  (Layer A)     │  │  (Layer B)     │  │ (Layer C)  │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│            Application Backend (FastAPI)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Emotion API │  │  Analytics   │  │ Safety Guard   │ │
│  │             │  │   Engine     │  │                │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Data Infrastructure                          │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │ PostgreSQL   │  │ Redis Cache │  │ S3/MinIO       │ │
│  │ (TimescaleDB)│  │             │  │ (optional)     │ │
│  └──────────────┘  └─────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Development Workflow

### 1. Backend Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/emotion/

# Start dev server
uvicorn cqox.main:app --reload
```

### 2. Frontend Development

```bash
cd frontend
npm install
npm run dev

# Build for production
npm run build
```

### 3. Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "add emotion tables"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📖 Documentation

- **[Full Specification](./docs/SPEC.md)** - 完全な仕様書 (PDF から変換)
- **[API Documentation](./docs/API.md)** - API エンドポイント詳細
- **[Frontend Components](./frontend/README.md)** - React コンポーネントガイド
- **[Data Generation](./scripts/README.md)** - CSV 生成ロジック詳細

---

## 🎓 Use Cases

### 1. 転職面接の準備

> 「面接で退職理由を聞かれると毎回泣いてしまう」

**使い方**:
1. 面接前に状態スライダーを入力 (不安度・泣きそう度)
2. 準備プラン (ジャーナリング・3つのメッセージ) を選択
3. シミュレーションで予測を確認
4. 面接後にアウトカムを記録 (実際の涙・伝達度)
5. ダッシュボードで「ジャーナリングをした時としない時の差」を確認

### 2. 上司との1on1

> 「評価面談で不満を伝えたいが、言葉が詰まって伝えられない」

**使い方**:
1. 目的関数スライダーで「伝えたい度」を高めに設定
2. 「3つのメッセージ」準備を重点実施
3. アウトカムで expression_score を記録
4. 分析: three_messages が expression_score にどれくらい効いているか確認

### 3. パートナーとの大事な話

> 「お金や将来の話をすると、関係が悪くなりそうで怖い」

**使い方**:
1. 目的関数で「関係維持」を最優先に設定
2. セーフワード (つらくなった時の合図) を事前に決める
3. relationship_impact を記録
4. 「関係を壊さずに本音を伝えるパターン」を探索

---

## 🤝 Contributing

Issues and PRs are welcome!

**開発の優先順位**:
1. 安全性・倫理の改善 (Safety module の精度向上)
2. 分析アルゴリズムの拡張 (Causal Forest, Synthetic Control など)
3. UI/UX の改善 (特にスライダーの分かりやすさ)
4. ドキュメント・例の追加

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

- **CQOx_gen** - ベースアーキテクチャとして利用
- **EconML / DoWhy** - 因果推論アルゴリズムの参考実装
- **いのちの電話** - 安全リソースとして掲載

---

## ⚠️ Disclaimer

Emotion CQOx is **NOT a medical device** and does **NOT provide diagnosis or treatment**.
If you are experiencing severe distress or suicidal thoughts, please contact professional resources immediately:

- **いのちの電話**: 0570-783-556 (24時間)
- **こころの健康相談統一ダイヤル**: 0570-064-556
- **Emergency**: 119 (Japan)

---

**Made with ❤️ for people who want to express themselves calmly**
