import React from "react";

const PARTNER_OPTIONS = [
  "面接官",
  "上司",
  "同僚",
  "クライアント",
  "家族",
  "友人",
  "恋人",
  "医師・カウンセラー",
  "その他",
];

type Props = {
  partnerRole: string;
  formality: number;
  disclosure: number;
  evalFocus: number;
  onPartnerRoleChange: (role: string) => void;
  onFormalityChange: (value: number) => void;
  onDisclosureChange: (value: number) => void;
  onEvalFocusChange: (value: number) => void;
};

const LabeledSlider = ({
  label,
  description,
  value,
  onChange,
}: {
  label: string;
  description: string;
  value: number;
  onChange: (v: number) => void;
}) => (
  <div className="space-y-2">
    <div>
      <p className="text-sm font-semibold text-gray-800">{label}</p>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
    <input type="range" min={0} max={10} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full" />
    <div className="flex justify-between text-[10px] text-gray-400">
      <span>0</span>
      <span>5</span>
      <span>10</span>
    </div>
  </div>
);

export const EpisodeContextSection: React.FC<Props> = ({
  partnerRole,
  formality,
  disclosure,
  evalFocus,
  onPartnerRoleChange,
  onFormalityChange,
  onDisclosureChange,
  onEvalFocusChange,
}) => (
  <section className="space-y-4">
    <h3 className="text-sm font-semibold text-gray-800">Layer C-: 今回の場面について</h3>
    <div className="space-y-4 bg-white rounded-2xl p-4 shadow-sm border border-gray-200">
      <div>
        <p className="text-sm font-semibold">誰に話す場面ですか？</p>
        <p className="text-xs text-gray-500 mb-2">一番近いものを選んでください。</p>
        <select
          value={partnerRole}
          onChange={(e) => onPartnerRoleChange(e.target.value)}
          className="w-full border rounded-md px-3 py-2"
        >
          {PARTNER_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <LabeledSlider
        label="どれくらいフォーマルな場面ですか？"
        description="0: ラフな会話 / 10: 非常に公式"
        value={formality}
        onChange={onFormalityChange}
      />
      <LabeledSlider
        label="どれくらい深い話になりそうですか？"
        description="0: 事務的 / 10: 心の核心まで話す"
        value={disclosure}
        onChange={onDisclosureChange}
      />
      <LabeledSlider
        label="どちらの評価が怖いですか？"
        description="0: 怒られる・否定される / 10: 褒められて目立つ"
        value={evalFocus}
        onChange={onEvalFocusChange}
      />
    </div>
  </section>
);
