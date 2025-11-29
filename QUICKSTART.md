# Emotion CQOx - Quick Start Guide

最速でEmotion CQOxを動かすためのガイド

---

## 🚀 5分で始める

### 1. サンプルデータ生成

```bash
cd /home/hirokionodera/CQOx_Emotion

# 仮想環境をアクティベート
source .venv/bin/activate

# サンプルCSV生成（既に生成済みならスキップ）
.venv/bin/python scripts/generate_emotion_cqox_sample.py \
  --n-rows 5000 \
  --seed 42 \
  --output sample/emotion_cqox_sample_5000.csv

# 生成確認
head -n 5 sample/emotion_cqox_sample_5000.csv
wc -l sample/emotion_cqox_sample_5000.csv
```

**期待される出力**:
```
✓ Wrote: sample/emotion_cqox_sample_5000.csv
  Rows: 5000
  Columns: 25
  Status distribution:
  {'completed': 3775, 'cancelled': 800, 'planned': 425}
```

### 2. バックエンド起動（開発モード）

```bash
cd backend

# 依存関係インストール（初回のみ）
pip install -r requirements.txt

# FastAPI起動
uvicorn cqox.main:app --reload --host 0.0.0.0 --port 8000
```

**確認**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. フロントエンド起動（開発モード）

```bash
cd frontend

# 依存関係インストール（初回のみ）
npm install

# 開発サーバー起動
npm run dev
```

**確認**:
- UI: http://localhost:5173

---

## 🐳 Docker で一発起動

```bash
# すべてのサービスを起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

**サービス**:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 📊 データ生成の詳細

### 生成パラメータ

```bash
python scripts/generate_emotion_cqox_sample.py \
  --n-rows 5000 \          # 行数
  --seed 42 \              # 乱数シード（再現性）
  --output path/to/output.csv
```

### 生成されるデータの特徴

1. **5000エピソード**
   - completed: 約75% (3,775行)
   - cancelled: 約16% (800行)
   - planned: 約9% (425行)

2. **ユーザー分布**
   - 30人のユーザー
   - user_id 1-5: ヘビーユーザー（出現頻度5倍）
   - user_id 6-30: 通常ユーザー

3. **scenario_type 分布**
   - interview: 25%
   - one_on_one: 20%
   - partner: 15%
   - family: 10%
   - friend: 10%
   - client: 10%
   - other: 10%

4. **擬似因果構造**
   ```
   準備 (journaling, three_messages, etc.)
     ↓ 正の効果
   ストレス軽減 (ΔStress)
   表現向上 (ΔExpression)
     ↓
   関係への影響 (relationship_impact)
   ```

5. **現実的な欠損**
   - 準備未実施: 空文字 "" (0ではない)
   - cancelled/planned: アウトカム列すべて空
   - reflection: 約70%のcompleted エピソードのみ

---

## 🔍 CSV検証コマンド

### Python で確認

```python
import pandas as pd

df = pd.read_csv("sample/emotion_cqox_sample_5000.csv")

# 基本統計
print(df.shape)  # (5000, 25)
print(df.columns)
print(df['status'].value_counts())

# 欠損率
print(df.isna().mean())

# completed のみ
completed = df[df['status'] == 'completed']
print(f"Completed: {len(completed)} rows")

# pre_anxiety と stress_after の差分（ΔStress）
completed['delta_stress'] = completed['pre_anxiety'] - completed['stress_after'].fillna(0)
print(completed['delta_stress'].describe())

# journaling_10m の有無で expression_score を比較
completed['has_journaling'] = completed['prep_journaling_10m_intensity'].fillna(0) > 0
print(completed.groupby('has_journaling')['expression_score'].describe())
```

### CLI で確認

```bash
# 行数
wc -l sample/emotion_cqox_sample_5000.csv

# カラム数
head -n 1 sample/emotion_cqox_sample_5000.csv | tr ',' '\n' | wc -l

# status の分布
cut -d, -f3 sample/emotion_cqox_sample_5000.csv | sort | uniq -c

# user_id の分布（ヘビーユーザーの確認）
cut -d, -f2 sample/emotion_cqox_sample_5000.csv | tail -n +2 | sort -n | uniq -c | sort -rn | head
```

---

## 🎯 API 使用例

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{"status": "healthy"}
```

### 2. Episode 作成（スライダー Layer A）

```bash
curl -X POST http://localhost:8000/api/emotion/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_type": "interview",
    "topic": "転職理由",
    "pre_anxiety": 7,
    "pre_crying_risk": 6,
    "pre_speech_block_risk": 8
  }'
```

### 3. Preference Profile 更新（スライダー Layer B）

```bash
curl -X POST http://localhost:8000/api/emotion/preferences/me \
  -H "Content-Type: application/json" \
  -d '{
    "weight_relief": 0.5,
    "weight_expression": 0.3,
    "weight_relationship": 0.2
  }'
```

### 4. シミュレーション（スライダー Layer C）

```bash
curl -X POST http://localhost:8000/api/emotion/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "pre_anxiety": 7,
    "pre_crying_risk": 6,
    "pre_speech_block_risk": 8,
    "prep_journaling_10m": 8,
    "prep_three_messages": 6,
    "prep_breathing_4_7_8": 5,
    "prep_roleplay_self_qa": 0,
    "prep_safe_word_plan": 0
  }'
```

**Response**:
```json
{
  "predicted_stress_after": {
    "mean": 4.2,
    "ci95": [2.1, 6.3]
  },
  "predicted_expression_score": {
    "mean": 6.5,
    "ci95": [4.0, 9.0]
  },
  "total_reward": 0.72,
  "disclaimer": "これは予測であり、保証ではありません..."
}
```

### 5. Safety Check

```bash
curl -X POST http://localhost:8000/api/emotion/safety/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "かなりつらいけど、なんとか頑張ります"
  }'
```

**Response (Safe)**:
```json
{
  "is_safe": true,
  "risk_level": "none",
  "triggers": [],
  "resources": []
}
```

**Response (High Risk)**:
```json
{
  "is_safe": false,
  "risk_level": "critical",
  "triggers": ["死にたい"],
  "message": "大変つらい状況だと思います...",
  "resources": [
    {
      "name": "いのちの電話",
      "phone": "0570-783-556",
      "url": "https://www.inochinodenwa.org/",
      "description": "24時間対応の電話相談"
    }
  ]
}
```

---

## 📊 スライダーUI の使い方

### Layer A: Episode Quick Sliders（状態入力）

```typescript
import { EpisodeQuickSliders } from './components/EpisodeQuickSliders';

<EpisodeQuickSliders
  preAnxiety={7}           // 今のしんどさ (0-10)
  preCryingRisk={6}        // 泣きそう度 (0-10)
  preSpeechBlockRisk={8}   // 言葉が詰まりそう (0-10)
  onChange={setPre}
/>
```

### Layer B: Preference Sliders（目的関数）

```typescript
import { PreferenceSliders } from './components/PreferenceSliders';

<PreferenceSliders
  relief={5}           // 楽さ重視度 (0-10)
  expression={7}       // 伝えたい度 (0-10)
  relationship={3}     // 関係維持度 (0-10)
  onChange={setPrefs}
/>
```

### Layer C: Simulation Panel（What-if）

```typescript
import { PreparationSimulator } from './components/PreparationSimulator';

  <PreparationSimulator
  preAnxiety={7}
  preCryingRisk={6}
  preSpeechBlockRisk={8}
  preferences={{ relief: 5, expression: 7, relationship: 3 }}
/>
```

---

## 🛠️ トラブルシューティング

### データ生成時のエラー

**Error: pandas not installed**
```bash
pip install pandas numpy scipy
```

**Permission denied**
```bash
chmod +x scripts/generate_emotion_cqox_sample.py
```

### Backend 起動時のエラー

**ModuleNotFoundError: No module named 'fastapi'**
```bash
cd backend
pip install -r requirements.txt
```

**Port 8000 already in use**
```bash
# 別のポートで起動
uvicorn cqox.main:app --port 8001
```

### Frontend 起動時のエラー

**npm install fails**
```bash
# キャッシュクリア
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Vite dev server エラー**
```bash
# ポート変更
npm run dev -- --port 3000
```

---

## 📝 次のステップ

1. **データ分析**
   ```bash
   cd backend
   python -m jupyter notebook
   # → notebooks/eda_emotion_cqox.ipynb を作成して分析
   ```

2. **カスタムデータ生成**
   ```bash
   # 10,000行、シード123で生成
   python scripts/generate_emotion_cqox_sample.py --n-rows 10000 --seed 123
   ```

3. **本番DB接続**
   - `backend/.env` ファイル作成
   - DATABASE_URL 設定
   - Alembic migration 実行

4. **認証追加**
   - JWT トークン実装
   - ユーザー登録/ログイン

5. **デプロイ**
   - Docker Compose で本番環境
   - Kubernetes manifest 作成（k8s/）

---

## 📚 参考ドキュメント

- [README.md](./README.md) - 全体概要
- [API Documentation](http://localhost:8000/docs) - FastAPI自動生成ドキュメント
- [PDF仕様書](./PDF/CQOx_gen 拡張案②.pdf) - 完全な仕様
- [CQOx_gen Repository](https://github.com/onodera22ten/CQOx_gen) - ベースアーキテクチャ

---

**Made with ❤️ for people who want to express themselves calmly**
