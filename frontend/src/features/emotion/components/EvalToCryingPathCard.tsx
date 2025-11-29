import React from "react";

export type PathSummary = {
  alpha_eval_to_stress: number;
  beta_eval_to_cry: number;
  beta_stress_to_cry: number;
  beta_suppress_to_cry: number;
  indirect_eval_to_cry: number;
  total_eval_to_cry: number;
  n_episodes: number;
  updated_at: string;
};

const describeValue = (value: number, positiveText: string, negativeText: string, neutral: string) => {
  if (value > 0.3) return positiveText;
  if (value < -0.3) return negativeText;
  return neutral;
};

export const EvalToCryingPathCard: React.FC<{ data?: PathSummary }> = ({ data }) => {
  if (!data) {
    return (
      <div className="border rounded-2xl p-4 shadow-sm bg-white">
        <h2 className="text-sm font-semibold mb-1">評価と涙の関係</h2>
        <p className="text-sm text-gray-500">まだ十分なデータがありません。</p>
      </div>
    );
  }

  const evalText = describeValue(
    data.total_eval_to_cry,
    "評価が厳しいほど涙レベルが上がる傾向があります。",
    "評価が厳しくても涙はむしろ下がる傾向があります。",
    "評価の厳しさと涙レベルの関係は小さいようです。"
  );

  const pathText = describeValue(
    data.indirect_eval_to_cry,
    "評価で感じるしんどさを通じて涙が高まる経路が大きいです。",
    "評価のしんどさが涙を下げる方向に働いています。",
    "評価 → しんどさ → 涙 の経路は今のところはっきりしません。"
  );

  const suppressText = describeValue(
    data.beta_suppress_to_cry,
    "「泣かないようにしよう」と思うほど逆に涙が増える傾向があります。",
    "抑え込もうとする意図は涙を下げる方向に働いています。",
    "抑え込みの意図と涙の関係は明確ではありません。"
  );

  const format = (value: number) => value?.toFixed(2);

  return (
    <div className="border rounded-2xl p-4 shadow-sm bg-white">
      <h2 className="text-sm font-semibold mb-1">評価と涙の関係（あなたのパターン）</h2>
      <p className="text-xs text-gray-500">
        {data.n_episodes} 件のエピソードから「評価の怖さ → しんどさ → 涙」の経路を推定しています。
      </p>
      <ul className="text-sm space-y-1 mt-3">
        <li>・評価→しんどさの影響: <b>{format(data.alpha_eval_to_stress)}</b></li>
        <li>・評価→涙の直接効果: <b>{format(data.beta_eval_to_cry)}</b></li>
        <li>・評価→しんどさ→涙の間接効果: <b>{format(data.indirect_eval_to_cry)}</b></li>
        <li>・合計効果: <b>{format(data.total_eval_to_cry)}</b></li>
        <li>・抑え込み→涙の影響: <b>{format(data.beta_suppress_to_cry)}</b></li>
      </ul>
      <div className="mt-3 text-sm space-y-1">
        <p>{evalText}</p>
        <p>{pathText}</p>
        <p>{suppressText}</p>
      </div>
      <p className="text-[10px] text-gray-400 mt-2">
        推定は既存データに基づく傾向であり、診断や保証ではありません。
      </p>
    </div>
  );
};
