/**
 * Preference Sliders (Layer B)
 *
 * User's objective function sliders
 * Maps to EmotionPreferenceProfile and reward function weights
 */

import React, { useMemo } from "react";

type Props = {
  relief: number; // 0-10
  expression: number; // 0-10
  relationship: number; // 0-10
  onChange: (values: {
    relief: number;
    expression: number;
    relationship: number;
  }) => void;
};

export const PreferenceSliders: React.FC<Props> = ({
  relief,
  expression,
  relationship,
  onChange,
}) => {
  // Auto-normalize to show percentages
  const total = useMemo(
    () => Math.max(relief + expression + relationship, 1),
    [relief, expression, relationship]
  );

  const normalized = {
    relief: relief / total,
    expression: expression / total,
    relationship: relationship / total,
  };

  return (
    <div className="space-y-6 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg shadow-sm">
      <div className="text-sm text-gray-700 mb-4">
        <strong>何を優先したいかをざっくり決めます</strong>
        <br />
        <span className="text-xs text-gray-500">
          （合計のバランスは自動で調整されます）
        </span>
      </div>

      <PrefSliderRow
        label="楽でいたい"
        description="しんどさをへらしたい"
        value={relief}
        share={normalized.relief}
        color="bg-green-500"
        onChange={(v) => onChange({ relief: v, expression, relationship })}
      />

      <PrefSliderRow
        label="ちゃんと伝えたい"
        description="本音や背景を伝えたい"
        value={expression}
        share={normalized.expression}
        color="bg-blue-500"
        onChange={(v) => onChange({ relief, expression: v, relationship })}
      />

      <PrefSliderRow
        label="関係をこわしたくない"
        description="できるだけ関係を大事にしたい"
        value={relationship}
        share={normalized.relationship}
        color="bg-purple-500"
        onChange={(v) => onChange({ relief, expression, relationship: v })}
      />

      <div className="mt-4 p-3 bg-white rounded border border-gray-200">
        <div className="text-xs text-gray-600 mb-2">配分イメージ:</div>
        <div className="flex h-2 rounded-full overflow-hidden">
          <div
            className="bg-green-500"
            style={{ width: `${normalized.relief * 100}%` }}
          />
          <div
            className="bg-blue-500"
            style={{ width: `${normalized.expression * 100}%` }}
          />
          <div
            className="bg-purple-500"
            style={{ width: `${normalized.relationship * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};

type PrefSliderRowProps = {
  label: string;
  description: string;
  value: number;
  share: number; // 0-1
  color: string;
  onChange: (v: number) => void;
};

const PrefSliderRow: React.FC<PrefSliderRowProps> = ({
  label,
  description,
  value,
  share,
  color,
  onChange,
}) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-gray-800">{label}</div>
          <div className="text-xs text-gray-500">{description}</div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-gray-800">
            {Math.round(share * 100)}%
          </div>
          <div className="text-xs text-gray-400">({value}/10)</div>
        </div>
      </div>
      <input
        type="range"
        min={0}
        max={10}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${color} opacity-70 hover:opacity-100 transition-opacity`}
      />
    </div>
  );
};
