import React, { useMemo, useState } from "react";

export type EpisodeDecomposition = {
  episode_id: number;
  observed_crying: number;
  predicted_crying: number;
  baseline_crying: number;
  contrib_trait: number;
  contrib_eval_threat: number;
  contrib_stress: number;
  contrib_suppress: number;
  contrib_preparations: number;
  beta_eval_to_cry: number;
  beta_stress_to_cry: number;
  beta_suppress_to_cry: number;
};

type WhatIfOption = {
  key: string;
  label: string;
  deltas: {
    eval?: number;
    stress?: number;
    suppress?: number;
    prep?: number;
  };
};

const whatIfOptions: WhatIfOption[] = [
  {
    key: "evalDown",
    label: "評価の怖さを3ポイント下げたら？",
    deltas: { eval: -3 },
  },
  {
    key: "suppressDown",
    label: "泣きを抑えようとする度合いを2ポイント下げたら？",
    deltas: { suppress: -2 },
  },
  {
    key: "prepPlus",
    label: "4-7-8呼吸を追加したら？（-0.5 相当）",
    deltas: { prep: -0.5 },
  },
];

export const EpisodeDecompositionCard: React.FC<{ data: EpisodeDecomposition }> = ({ data }) => {
  const [active, setActive] = useState<string | null>(null);

  const deltas = useMemo(() => {
    const option = whatIfOptions.find((o) => o.key === active);
    return option?.deltas ?? {};
  }, [active]);

  const adjusted = useMemo(() => {
    const evalDelta = (deltas.eval ?? 0) * data.beta_eval_to_cry;
    const stressDelta = (deltas.stress ?? 0) * data.beta_stress_to_cry;
    const suppressDelta = (deltas.suppress ?? 0) * data.beta_suppress_to_cry;
    const prepDelta = deltas.prep ?? 0;
    const predicted =
      data.baseline_crying +
      data.contrib_trait +
      (data.contrib_eval_threat + evalDelta) +
      (data.contrib_stress + stressDelta) +
      (data.contrib_suppress + suppressDelta) +
      (data.contrib_preparations + prepDelta);

    return {
      contrib_eval: data.contrib_eval_threat + evalDelta,
      contrib_stress: data.contrib_stress + stressDelta,
      contrib_suppress: data.contrib_suppress + suppressDelta,
      contrib_prep: data.contrib_preparations + prepDelta,
      predicted,
    };
  }, [data, deltas]);

  const rows = [
    { label: "ベースライン", value: data.baseline_crying },
    { label: "＋特性（泣きやすさ）", value: data.contrib_trait },
    { label: "＋評価の怖さ", value: active ? adjusted.contrib_eval : data.contrib_eval_threat },
    { label: "＋今のしんどさ", value: active ? adjusted.contrib_stress : data.contrib_stress },
    { label: "＋泣きを抑えたい度", value: active ? adjusted.contrib_suppress : data.contrib_suppress },
    { label: "＋今回の準備", value: active ? adjusted.contrib_prep : data.contrib_preparations },
  ];

  const finalPred = active ? adjusted.predicted : data.predicted_crying;
  const diff = data.observed_crying - finalPred;

  return (
    <div className="border rounded-2xl p-4 shadow-sm bg-white space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-gray-900">今回の涙レベルを分解する</h2>
        <p className="text-xs text-gray-500">
          モデルが推定した「ベースライン」に各要素を足し合わせたときの変化をウォーターフォール形式で表示します。
        </p>
      </div>
      <div className="space-y-2">
        {rows.map((row) => (
          <div key={row.label} className="flex justify-between text-xs">
            <span className="text-gray-600">{row.label}</span>
            <span className="font-semibold">{row.value.toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between text-sm border-t border-dashed pt-2">
          <span className="font-semibold text-gray-700">予測された涙レベル</span>
          <span className="font-semibold">{finalPred.toFixed(2)}</span>
        </div>
        <div className="text-xs text-gray-500">
          実際の涙レベル: <b>{data.observed_crying.toFixed(1)}</b> / 差分:{" "}
          <b>{diff >= 0 ? "+" : ""}
            {diff.toFixed(2)}</b>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-gray-700">What-if</h3>
        <div className="space-y-2">
          {whatIfOptions.map((option) => (
            <button
              key={option.key}
              className={`w-full text-left text-xs rounded-lg border px-3 py-2 transition ${
                active === option.key ? "border-blue-500 bg-blue-50 text-blue-700" : "border-gray-200 hover:border-gray-300"
              }`}
              onClick={() => setActive((prev) => (prev === option.key ? null : option.key))}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
      {active && (
        <p className="text-[10px] text-gray-400">
          What-if はモデル係数に基づく簡易推定です。感覚を掴むための参考としてご利用ください。
        </p>
      )}
    </div>
  );
};
