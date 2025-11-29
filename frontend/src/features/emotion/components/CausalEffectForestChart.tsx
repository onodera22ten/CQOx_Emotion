import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ErrorBar,
} from "recharts";

export type EffectDatum = {
  treatment_key: string;
  outcome_name: string;
  ate: number;
  ci_lower: number | null;
  ci_upper: number | null;
};

type Props = {
  data: EffectDatum[];
  outcomeName: string;
};

const treatmentLabel = (key: string) => {
  switch (key) {
    case "journaling_10m":
      return "10分の書き出し";
    case "three_messages":
      return "伝えたい3つのメッセージ";
    case "breathing_4_7_8":
      return "4-7-8呼吸法";
    case "roleplay_self_qa":
      return "自分でQ&Aロールプレイ";
    case "safe_word_plan":
      return "セーフワードプラン";
    default:
      return key;
  }
};

const outcomeLabel = (key: string) => {
  switch (key) {
    case "crying_level":
      return "涙レベル";
    case "stress_after":
      return "終わった後の楽さ";
    case "expression_score":
      return "伝えられた感";
    case "relationship_impact":
      return "関係への影響";
    default:
      return key;
  }
};

export const CausalEffectForestChart: React.FC<Props> = ({ data, outcomeName }) => {
  const filtered = data.filter((d) => d.outcome_name === outcomeName);
  const chartData = filtered.map((d) => {
    const ciLow = d.ci_lower ?? d.ate;
    const ciHigh = d.ci_upper ?? d.ate;
    return {
      name: treatmentLabel(d.treatment_key),
      ate: d.ate,
      errLow: d.ate - ciLow,
      errHigh: ciHigh - d.ate,
    };
  });

  if (chartData.length === 0) {
    return (
      <div className="p-4 border rounded-2xl bg-white shadow-sm">
        <h3 className="text-sm font-semibold mb-2">
          {outcomeLabel(outcomeName)} に対する効果
        </h3>
        <p className="text-sm text-gray-500">まだ十分なデータがありません。</p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-2xl bg-white shadow-sm">
      <h3 className="text-sm font-semibold mb-2">
        {outcomeLabel(outcomeName)} に対する準備ごとの推定効果
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 24, left: 80, bottom: 10 }}
          >
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" />
            <Tooltip />
            <ReferenceLine x={0} strokeDasharray="3 3" />
            <Bar dataKey="ate" fill="#3b82f6">
              <ErrorBar
                dataKey="ate"
                width={6}
                data={chartData.map((d) => ({
                  x: d.ate,
                  low: d.ate - d.errLow,
                  high: d.ate + d.errHigh,
                }))}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        棒は推定平均効果、線は95%信頼区間です。0を跨ぐ場合は効果が不確かです。
      </p>
    </div>
  );
};
