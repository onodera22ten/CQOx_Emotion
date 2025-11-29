import React from "react";

type Props = {
  evalThreat: number;
  suppressIntent: number;
  onEvalThreatChange: (value: number) => void;
  onSuppressIntentChange: (value: number) => void;
};

const SliderRow: React.FC<{
  label: string;
  value: number;
  onChange: (v: number) => void;
  help?: string;
}> = ({ label, value, onChange, help }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-sm font-medium text-gray-700">
      <span>{label}</span>
      <span>{value}</span>
    </div>
    {help && <p className="text-xs text-gray-500">{help}</p>}
    <input
      type="range"
      min={0}
      max={10}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full"
    />
    <div className="flex justify-between text-[10px] text-gray-400">
      <span>0</span>
      <span>5</span>
      <span>10</span>
    </div>
  </div>
);

export const EvaluationContextSliders: React.FC<Props> = ({
  evalThreat,
  suppressIntent,
  onEvalThreatChange,
  onSuppressIntentChange,
}) => {
  return (
    <div className="space-y-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
      <div>
        <h3 className="text-sm font-semibold text-gray-800">評価コンテキスト</h3>
        <p className="text-xs text-gray-500">
          今回の相手や場面をどのくらい厳しく感じているか、どれくらい泣きを抑えたいかを教えてください。
        </p>
      </div>
      <SliderRow
        label="評価されそうな怖さ"
        value={evalThreat}
        onChange={onEvalThreatChange}
        help="「厳しく見られそう」「失敗したくない」と感じる度合い"
      />
      <SliderRow
        label="泣きを抑えたい度"
        value={suppressIntent}
        onChange={onSuppressIntentChange}
        help="どれくらい『泣いてはいけない』と強く思っているか"
      />
    </div>
  );
};
