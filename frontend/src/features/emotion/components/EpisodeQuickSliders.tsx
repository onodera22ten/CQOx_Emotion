/**
 * Episode Quick Sliders (Layer A)
 *
 * Pre-episode state sliders for quick input without heavy text writing
 * Maps directly to pre_anxiety, pre_crying_risk, pre_speech_block_risk
 */

import React from "react";

type Props = {
  preAnxiety: number;
  preCryingRisk: number;
  preSpeechBlockRisk: number;
  onChange: (values: {
    preAnxiety: number;
    preCryingRisk: number;
    preSpeechBlockRisk: number;
  }) => void;
};

export const EpisodeQuickSliders: React.FC<Props> = ({
  preAnxiety,
  preCryingRisk,
  preSpeechBlockRisk,
  onChange,
}) => {
  return (
    <div className="space-y-6 p-4 bg-white rounded-lg shadow-sm">
      <div className="text-sm text-gray-600 mb-4">
        今の状態をスライダーで教えてください（テキストは不要です）
      </div>

      <SliderRow
        label="今のしんどさ"
        emojiLow="🙂"
        emojiHigh="😣"
        value={preAnxiety}
        onChange={(v) =>
          onChange({ preAnxiety: v, preCryingRisk, preSpeechBlockRisk })
        }
      />

      <SliderRow
        label="泣きそう度"
        emojiLow="🙂"
        emojiHigh="😭"
        value={preCryingRisk}
        onChange={(v) =>
          onChange({ preAnxiety, preCryingRisk: v, preSpeechBlockRisk })
        }
      />

      <SliderRow
        label="言葉が詰まりそう"
        emojiLow="🗣️"
        emojiHigh="😶"
        value={preSpeechBlockRisk}
        onChange={(v) =>
          onChange({ preAnxiety, preCryingRisk, preSpeechBlockRisk: v })
        }
      />
    </div>
  );
};

type SliderRowProps = {
  label: string;
  emojiLow: string;
  emojiHigh: string;
  value: number;
  onChange: (v: number) => void;
};

const SliderRow: React.FC<SliderRowProps> = ({
  label,
  emojiLow,
  emojiHigh,
  value,
  onChange,
}) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center justify-between text-sm font-medium">
        <span className="text-gray-700">{label}</span>
        <span className="text-sm text-gray-500 font-semibold">
          {value}
        </span>
      </div>
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{emojiLow}</span>
        <input
          type="range"
          min={0}
          max={10}
          step={1}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
                     slider-thumb:appearance-none slider-thumb:w-4 slider-thumb:h-4
                     slider-thumb:bg-blue-600 slider-thumb:rounded-full slider-thumb:cursor-pointer
                     hover:bg-gray-300 transition-colors"
        />
        <span className="text-2xl">{emojiHigh}</span>
      </div>
      <div className="flex justify-between text-xs text-gray-400 px-8">
        <span>0</span>
        <span>5</span>
        <span>10</span>
      </div>
    </div>
  );
};
