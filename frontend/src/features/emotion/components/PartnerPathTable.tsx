import React from "react";

export type PartnerPathRow = {
  partner_role: string;
  total_eval_to_cry: number | null;
  n_episodes: number;
  updated_at: string;
};

export const PartnerPathTable: React.FC<{ rows: PartnerPathRow[] }> = ({ rows }) => {
  if (!rows.length) {
    return (
      <div className="border rounded-2xl p-4 shadow-sm bg-white">
        <h2 className="text-sm font-semibold mb-2">相手別：評価と涙の関係</h2>
        <p className="text-sm text-gray-500">まだ十分なデータがありません。</p>
      </div>
    );
  }

  return (
    <div className="border rounded-2xl p-4 shadow-sm bg-white">
      <h2 className="text-sm font-semibold mb-2">相手別：評価と涙の関係</h2>
      <p className="text-xs text-gray-600 mb-3">相手のタイプごとに「評価の怖さ → 涙」の合計効果を推定しています。</p>
      <table className="w-full text-xs">
        <thead>
          <tr className="text-gray-500">
            <th className="text-left py-1">相手</th>
            <th className="text-right py-1">効果</th>
            <th className="text-right py-1">Episode</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.partner_role} className="border-t border-gray-100">
              <td className="py-1">{row.partner_role}</td>
              <td className="py-1 text-right font-semibold">
                {row.total_eval_to_cry !== null ? row.total_eval_to_cry.toFixed(2) : "—"}
              </td>
              <td className="py-1 text-right text-gray-500">{row.n_episodes}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-[10px] text-gray-400 mt-2">10 件以上のエピソードがある相手タイプのみ表示しています。</p>
    </div>
  );
};
