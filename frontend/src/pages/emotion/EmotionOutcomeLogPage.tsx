import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";

type Episode = {
  id: number;
  topic: string;
  scheduled_at: string;
  status: string;
};

const defaultForm = {
  stress_during: 5,
  stress_after: 4,
  crying_level: 3,
  speech_block_level: 3,
  expression_score: 6,
  relationship_impact: 0,
  partner_reaction: "neutral",
  days_after_reflection: 0,
  would_repeat_preparation: 5,
  reflection_short: "",
};

export const EmotionOutcomeLogPage: React.FC = () => {
  const [form, setForm] = useState(defaultForm);
  const [selectedEpisode, setSelectedEpisode] = useState<number | null>(null);

  const episodesQuery = useQuery({
    queryKey: ["emotion", "episodes"],
    queryFn: () => apiFetch<Episode[]>("/api/emotion/episodes?limit=50"),
  });

  const mutation = useMutation({
    mutationFn: () => {
      if (!selectedEpisode) {
        throw new Error("Episode not selected");
      }
      return apiFetch(`/api/emotion/episodes/${selectedEpisode}/outcome`, {
        method: "POST",
        body: JSON.stringify(form),
      });
    },
    onSuccess: () => {
      alert("アウトカムを記録しました。ダッシュボードで確認できます。");
      setForm(defaultForm);
    },
  });

  const options = useMemo(() => {
    return (episodesQuery.data || []).map((ep) => ({
      value: ep.id,
      label: `${new Date(ep.scheduled_at).toLocaleDateString()} / ${ep.topic} (${ep.status})`,
    }));
  }, [episodesQuery.data]);

  const canSubmit = selectedEpisode !== null && !mutation.isPending;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Outcome Log</h1>
        <p className="text-sm text-gray-500">Episode の終了後に結果を記録し、因果推定に回します。</p>
      </div>
      <div className="bg-white border rounded-2xl shadow-sm p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Episode を選択</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={selectedEpisode ?? ""}
            onChange={(e) => setSelectedEpisode(Number(e.target.value))}
          >
            <option value="" disabled>
              Episode を選択してください
            </option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {["stress_during", "stress_after", "crying_level", "speech_block_level", "expression_score"].map(
            (key) => (
              <NumberInput
                key={key}
                label={labelForKey(key)}
                value={form[key as keyof typeof form] as number}
                onChange={(val) => setForm((prev) => ({ ...prev, [key]: val }))}
                min={0}
                max={10}
              />
            )
          )}
          <NumberInput
            label="関係への影響 (-5〜+5)"
            value={form.relationship_impact}
            onChange={(val) => setForm((prev) => ({ ...prev, relationship_impact: val }))}
            min={-5}
            max={5}
          />
          <NumberInput
            label="振り返り (日数)"
            value={form.days_after_reflection}
            onChange={(val) => setForm((prev) => ({ ...prev, days_after_reflection: val }))}
            min={0}
            max={30}
          />
          <NumberInput
            label="この準備をまたやりたい度 (0-10)"
            value={form.would_repeat_preparation}
            onChange={(val) => setForm((prev) => ({ ...prev, would_repeat_preparation: val }))}
            min={0}
            max={10}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">振り返りメモ（任意）</label>
          <textarea
            className="w-full border rounded-lg px-3 py-2"
            rows={3}
            value={form.reflection_short}
            onChange={(e) => setForm((prev) => ({ ...prev, reflection_short: e.target.value }))}
          />
        </div>
        <button
          className="w-full md:w-auto px-6 py-3 rounded-lg bg-blue-600 text-white font-semibold disabled:opacity-50"
          disabled={!canSubmit}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? "送信中..." : "アウトカムを保存する"}
        </button>
      </div>
    </div>
  );
};

const NumberInput = ({
  label,
  value,
  onChange,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
}) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
    <input
      type="number"
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full border rounded-lg px-3 py-2"
    />
  </div>
);

const labelForKey = (key: string) => {
  switch (key) {
    case "stress_during":
      return "話している最中のしんどさ (0-10)";
    case "stress_after":
      return "終わった後のしんどさ (0-10)";
    case "crying_level":
      return "涙レベル (0-10)";
    case "speech_block_level":
      return "言葉が詰まった度 (0-10)";
    case "expression_score":
      return "伝えられた感 (0-10)";
    default:
      return key;
  }
};
