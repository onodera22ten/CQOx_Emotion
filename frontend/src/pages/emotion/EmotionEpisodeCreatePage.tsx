import React, { useState } from "react";
import { EpisodeQuickSliders } from "@/features/emotion/components/EpisodeQuickSliders";
import { PreferenceSliders } from "@/features/emotion/components/PreferenceSliders";
import { PreparationSimulator } from "@/features/emotion/components/PreparationSimulator";
import { EvaluationContextSliders } from "@/features/emotion/components/EvaluationContextSliders";

export const EmotionEpisodeCreatePage: React.FC = () => {
  const [pre, setPre] = useState({
    preAnxiety: 5,
    preCryingRisk: 5,
    preSpeechBlockRisk: 5,
  });

  const [prefs, setPrefs] = useState({
    relief: 5,
    expression: 5,
    relationship: 5,
  });

  const [evalContext, setEvalContext] = useState({
    evalThreat: 5,
    suppressIntent: 5,
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Episode Draft</h1>
        <p className="text-sm text-gray-500">
          Layer A/B/C のスライダーで「今回の準備プラン」を数クリックで保存できます。
        </p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Layer A: 今の状態</h2>
            <EpisodeQuickSliders
              preAnxiety={pre.preAnxiety}
              preCryingRisk={pre.preCryingRisk}
              preSpeechBlockRisk={pre.preSpeechBlockRisk}
              onChange={setPre}
            />
          </section>
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Layer B: 目的関数</h2>
            <PreferenceSliders
              relief={prefs.relief}
              expression={prefs.expression}
              relationship={prefs.relationship}
              onChange={setPrefs}
            />
          </section>
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Layer B+: 評価の怖さ</h2>
            <EvaluationContextSliders
              evalThreat={evalContext.evalThreat}
              suppressIntent={evalContext.suppressIntent}
              onEvalThreatChange={(v) => setEvalContext((prev) => ({ ...prev, evalThreat: v }))}
              onSuppressIntentChange={(v) =>
                setEvalContext((prev) => ({ ...prev, suppressIntent: v }))
              }
            />
          </section>
        </div>
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Layer C: 準備プラン</h2>
          <PreparationSimulator
            preAnxiety={pre.preAnxiety}
            preCryingRisk={pre.preCryingRisk}
            preSpeechBlockRisk={pre.preSpeechBlockRisk}
            preferences={prefs}
            evalThreat={evalContext.evalThreat}
            suppressIntent={evalContext.suppressIntent}
          />
        </section>
      </div>
    </div>
  );
};
