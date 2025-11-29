import React from "react";

export type SummaryStats = {
  total_episodes: number;
  total_completed: number;
  total_planned: number;
  by_preparation: { template_key: string; count: number }[];
};

const templateLabel = (key: string) => {
  switch (key) {
    case "journaling_10m":
      return "10分の書き出し";
    case "three_messages":
      return "3メッセージ";
    case "breathing_4_7_8":
      return "4-7-8呼吸";
    case "roleplay_self_qa":
      return "セルフQ&A";
    case "safe_word_plan":
      return "セーフワード";
    default:
      return key;
  }
};

type Props = {
  summary: SummaryStats;
};

export const EffectSummaryCards: React.FC<Props> = ({ summary }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <SummaryCard label="総エピソード" value={summary.total_episodes} />
      <SummaryCard label="完了済み" value={summary.total_completed} />
      <SummaryCard label="計画中" value={summary.total_planned} />
      <div className="md:col-span-3 p-4 border rounded-2xl bg-white shadow-sm">
        <div className="text-sm font-semibold text-gray-700 mb-2">
          よく実施している準備
        </div>
        <div className="flex flex-wrap gap-3">
          {summary.by_preparation.map((item) => (
            <span
              key={item.template_key}
              className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-sm text-blue-700 border border-blue-200"
            >
              {templateLabel(item.template_key)} <span className="ml-2 font-semibold">{item.count}</span>
            </span>
          ))}
          {summary.by_preparation.length === 0 && (
            <span className="text-sm text-gray-500">まだ準備の記録がありません。</span>
          )}
        </div>
      </div>
    </div>
  );
};

const SummaryCard = ({ label, value }: { label: string; value: number }) => (
  <div className="p-4 border rounded-2xl bg-white shadow-sm">
    <div className="text-xs text-gray-500">{label}</div>
    <div className="text-2xl font-semibold text-gray-900">{value}</div>
  </div>
);
