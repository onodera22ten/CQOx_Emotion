/**
 * Simulation Panel (Layer C)
 *
 * What-if simulation for preparation plans
 * Shows predicted outcomes based on generative model
 */

import React, { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";

type SimulationRequest = {
  preAnxiety: number;
  preCryingRisk: number;
  preSpeechBlockRisk: number;
  prepJournaling10m: number;
  prepThreeMessages: number;
  prepBreathing478: number;
  prepRoleplaySelfQa: number;
  prepSafeWordPlan: number;
};

type DeltaMetric = {
  mean: number;
  ci95: [number, number];
};

type SimulationResponse = {
  predictedStressAfter: DeltaMetric;
  predictedCryingLevel: DeltaMetric;
  predictedExpressionScore: DeltaMetric;
  predictedRelationshipImpact: DeltaMetric;
  totalReward: number;
  disclaimer: string;
};

type Props = {
  preAnxiety: number;
  preCryingRisk: number;
  preSpeechBlockRisk: number;
  preferences: {
    relief: number;
    expression: number;
    relationship: number;
  };
};

export const PreparationSimulator: React.FC<Props> = ({
  preAnxiety,
  preCryingRisk,
  preSpeechBlockRisk,
  preferences,
}) => {
  const defaultDate = new Date();
  defaultDate.setHours(defaultDate.getHours() + 1);
  const [scenarioDetails, setScenarioDetails] = useState({
    scenarioType: "other",
    topic: "",
    scheduledAt: defaultDate.toISOString().slice(0, 16),
    location: "online",
  });
  const [preparations, setPreparations] = useState({
    journaling: 0,
    threeMessages: 0,
    breathing: 0,
    roleplay: 0,
    safeWord: 0,
  });

  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [simulationOnly, setSimulationOnly] = useState(false);
  const [savedEpisodeId, setSavedEpisodeId] = useState<number | null>(null);

  // Mutation for saving episode draft
  const saveEpisodeDraftMutation = useMutation({
    mutationFn: async (payload: any) =>
      apiFetch("/api/emotion/episodes/draft", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      setSavedEpisodeId(data.episode_id);
      alert(`準備プランを保存しました (Episode ID: ${data.episode_id})\n\n${data.message}`);
    },
    onError: (error: Error) => {
      alert(`保存に失敗しました: ${error.message}`);
    },
  });

  const handleScenarioChange = (field: keyof typeof scenarioDetails) => (value: string) => {
    setScenarioDetails((prev) => ({ ...prev, [field]: value }));
  };

  const handleSavePlan = () => {
    const topic = scenarioDetails.topic.trim() || "未設定";
    const location = scenarioDetails.location.trim() || "online";
    const parsedDate = new Date(scenarioDetails.scheduledAt);
    const scheduledAt = Number.isNaN(parsedDate.getTime())
      ? new Date().toISOString()
      : parsedDate.toISOString();

    const payload = {
      scenario_type: scenarioDetails.scenarioType,
      topic,
      scheduled_at: scheduledAt,
      location,
      pre_state: {
        pre_anxiety: preAnxiety,
        pre_crying_risk: preCryingRisk,
        pre_speech_block_risk: preSpeechBlockRisk,
      },
      preparations_planned: {
        journaling_10m: preparations.journaling,
        three_messages: preparations.threeMessages,
        breathing_4_7_8: preparations.breathing,
        roleplay_self_qa: preparations.roleplay,
        safe_word_plan: preparations.safeWord,
      },
      preference_weights_raw: {
        relief: preferences.relief,
        expression: preferences.expression,
        relationship: preferences.relationship,
      },
    };

    saveEpisodeDraftMutation.mutate(payload);
  };

  const runSimulation = async () => {
    setIsLoading(true);

    // In real implementation, call API
    // const response = await fetch('/api/emotion/simulate', {...})

    // Mock simulation for demo
    await new Promise(resolve => setTimeout(resolve, 500));

    const totalPrep = (
      0.25 * preparations.journaling +
      0.35 * preparations.threeMessages +
      0.20 * preparations.breathing +
      0.25 * preparations.roleplay
    ) / 10.0;

    const stressAfter = Math.max(preAnxiety - 1.0 - 1.5 * totalPrep, 0);
    const expression = Math.min(
      5.0 + 0.4 * preparations.threeMessages / 2 + 0.3 * preparations.roleplay / 2,
      10
    );

    setSimulation({
      predictedStressAfter: {
        mean: stressAfter,
        ci95: [Math.max(stressAfter - 2, 0), Math.min(stressAfter + 2, 10)],
      },
      predictedCryingLevel: {
        mean: preCryingRisk - 0.3 * preparations.journaling / 2,
        ci95: [0, 10],
      },
      predictedExpressionScore: {
        mean: expression,
        ci95: [Math.max(expression - 2.5, 0), Math.min(expression + 2.5, 10)],
      },
      predictedRelationshipImpact: {
        mean: -1 + 0.4 * (expression - 5) / 2,
        ci95: [-5, 5],
      },
      totalReward: 0.65,
      disclaimer: "これは予測であり、保証ではありません。",
    });

    setIsLoading(false);
  };

  useEffect(() => {
    runSimulation();
  }, [preparations, preAnxiety, preCryingRisk, preferences]);

  return (
    <div className="space-y-6 p-4 bg-white rounded-lg shadow-md border border-gray-200">
      <div className="border-b pb-3 space-y-3">
        <h3 className="text-lg font-semibold text-gray-800">
          📊 準備プランのシミュレーション
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          準備スライダーを動かして、結果の予測を見てみましょう
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-gray-50 rounded-lg p-3 text-sm">
          <div>
            <label className="block text-gray-600 mb-1">シナリオタイプ</label>
            <select
              value={scenarioDetails.scenarioType}
              onChange={(e) => handleScenarioChange("scenarioType")(e.target.value)}
              className="w-full border rounded-md px-2 py-1"
            >
              <option value="interview">面接 / 評価</option>
              <option value="one_on_one">1on1</option>
              <option value="partner">パートナー</option>
              <option value="family">家族</option>
              <option value="friend">友人</option>
              <option value="client">クライアント</option>
              <option value="other">その他</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600 mb-1">トピック</label>
            <input
              type="text"
              value={scenarioDetails.topic}
              onChange={(e) => handleScenarioChange("topic")(e.target.value)}
              placeholder="例: 評価面談のフィードバック"
              className="w-full border rounded-md px-2 py-1"
            />
          </div>
          <div>
            <label className="block text-gray-600 mb-1">予定日時</label>
            <input
              type="datetime-local"
              value={scenarioDetails.scheduledAt}
              onChange={(e) => handleScenarioChange("scheduledAt")(e.target.value)}
              className="w-full border rounded-md px-2 py-1"
            />
          </div>
          <div>
            <label className="block text-gray-600 mb-1">場所 / チャンネル</label>
            <input
              type="text"
              value={scenarioDetails.location}
              onChange={(e) => handleScenarioChange("location")(e.target.value)}
              placeholder="オンライン / オフィス / カフェ など"
              className="w-full border rounded-md px-2 py-1"
            />
          </div>
        </div>
      </div>

      {/* Preparation Sliders */}
      <div className="space-y-3">
        <PrepSlider
          label="10分の書き出し"
          value={preparations.journaling}
          onChange={(v) => setPreparations({ ...preparations, journaling: v })}
        />
        <PrepSlider
          label="伝えたい3つのメッセージ"
          value={preparations.threeMessages}
          onChange={(v) => setPreparations({ ...preparations, threeMessages: v })}
        />
        <PrepSlider
          label="4-7-8呼吸法"
          value={preparations.breathing}
          onChange={(v) => setPreparations({ ...preparations, breathing: v })}
        />
        <PrepSlider
          label="自分でQ&Aロールプレイ"
          value={preparations.roleplay}
          onChange={(v) => setPreparations({ ...preparations, roleplay: v })}
        />
        <PrepSlider
          label="セーフワードを決める"
          value={preparations.safeWord}
          onChange={(v) => setPreparations({ ...preparations, safeWord: v })}
        />
      </div>

      {/* Simulation Results */}
      {simulation && !isLoading && (
        <div className="space-y-4 pt-4 border-t">
          <div className="text-sm font-semibold text-gray-700 mb-3">
            予測される結果:
          </div>

          <ResultBar
            label="終わった後の楽さ"
            value={10 - simulation.predictedStressAfter.mean}
            max={10}
            color="bg-green-500"
            ci={[
              10 - simulation.predictedStressAfter.ci95[1],
              10 - simulation.predictedStressAfter.ci95[0],
            ]}
          />

          <ResultBar
            label="伝えられた感"
            value={simulation.predictedExpressionScore.mean}
            max={10}
            color="bg-blue-500"
            ci={simulation.predictedExpressionScore.ci95}
          />

          <ResultBar
            label="関係への影響"
            value={simulation.predictedRelationshipImpact.mean + 5}
            max={10}
            color="bg-purple-500"
            ci={[
              simulation.predictedRelationshipImpact.ci95[0] + 5,
              simulation.predictedRelationshipImpact.ci95[1] + 5,
            ]}
          />

          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <div className="text-xs text-yellow-800">
              ⚠️ {simulation.disclaimer}
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Save Button and Simulation Only Mode */}
      <div className="pt-4 border-t space-y-3">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="simulation-only"
            checked={simulationOnly}
            onChange={(e) => setSimulationOnly(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="simulation-only" className="text-sm text-gray-700">
            今回はログを残さず、シミュレーションだけ行う
          </label>
        </div>

        {!simulationOnly && (
          <button
            onClick={handleSavePlan}
            disabled={saveEpisodeDraftMutation.isPending || savedEpisodeId !== null}
            className={`w-full px-4 py-3 rounded-lg font-semibold text-white transition-colors ${
              savedEpisodeId !== null
                ? "bg-green-600 cursor-default"
                : saveEpisodeDraftMutation.isPending
                ? "bg-gray-400 cursor-wait"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {saveEpisodeDraftMutation.isPending
              ? "保存中..."
              : savedEpisodeId !== null
              ? `✓ 保存済み (ID: ${savedEpisodeId})`
              : "今回の準備プランを保存する"}
          </button>
        )}

        {simulationOnly && (
          <div className="text-sm text-gray-500 text-center py-2">
            シミュレーションのみモード（保存しません）
          </div>
        )}

        {savedEpisodeId !== null && (
          <div className="text-xs text-green-700 bg-green-50 border border-green-200 rounded p-2">
            ✓ このプランは保存されました。後日、結果を記録できます。
          </div>
        )}
      </div>
    </div>
  );
};

type PrepSliderProps = {
  label: string;
  value: number;
  onChange: (v: number) => void;
};

const PrepSlider: React.FC<PrepSliderProps> = ({ label, value, onChange }) => {
  return (
    <div className="flex items-center space-x-3">
      <div className="flex-1">
        <div className="text-xs text-gray-600 mb-1">{label}</div>
        <input
          type="range"
          min={0}
          max={10}
          step={1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>
      <div className="text-sm font-semibold text-gray-700 w-8 text-right">
        {value}
      </div>
    </div>
  );
};

type ResultBarProps = {
  label: string;
  value: number;
  max: number;
  color: string;
  ci: [number, number];
};

const ResultBar: React.FC<ResultBarProps> = ({ label, value, max, color, ci }) => {
  const percentage = (value / max) * 100;
  const ciLowPct = (ci[0] / max) * 100;
  const ciHighPct = (ci[1] / max) * 100;

  return (
    <div>
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>{label}</span>
        <span>{value.toFixed(1)} / {max}</span>
      </div>
      <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden">
        {/* CI range */}
        <div
          className="absolute h-full bg-gray-300 opacity-30"
          style={{
            left: `${ciLowPct}%`,
            width: `${ciHighPct - ciLowPct}%`,
          }}
        />
        {/* Mean value */}
        <div
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
