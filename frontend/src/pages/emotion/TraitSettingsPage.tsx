import React, { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";

type TraitProfile = {
  trait_social_anxiety: number;
  trait_crying_proneness: number;
  trait_suppression: number;
};

const SliderRow = ({
  label,
  value,
  onChange,
  help,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  help?: string;
}) => (
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
  </div>
);

export const TraitSettingsPage: React.FC = () => {
  const query = useQuery({
    queryKey: ["emotion", "traits"],
    queryFn: () => apiFetch<TraitProfile>("/api/emotion/traits/me"),
  });

  const [form, setForm] = useState<TraitProfile>({
    trait_social_anxiety: 5,
    trait_crying_proneness: 5,
    trait_suppression: 5,
  });

  useEffect(() => {
    if (query.data) {
      setForm(query.data);
    }
  }, [query.data]);

  const mutation = useMutation({
    mutationFn: (payload: TraitProfile) =>
      apiFetch<TraitProfile>("/api/emotion/traits/me", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      setForm(data);
      alert("更新しました");
    },
    onError: (error: Error) => {
      alert(`更新に失敗しました: ${error.message}`);
    },
  });

  if (query.isLoading) {
    return <div className="text-sm text-gray-500">読み込み中...</div>;
  }

  return (
    <div className="space-y-6 max-w-lg">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Trait 設定</h1>
        <p className="text-sm text-gray-500">
          普段の自分の傾向をざっくり入力すると、因果推定で補正に使われます。
          医療・診断目的ではありません。
        </p>
      </div>

      <div className="space-y-5 bg-white p-5 rounded-2xl border border-gray-200 shadow-sm">
        <SliderRow
          label="人前で話すときの不安の強さ"
          value={form.trait_social_anxiety}
          help="普段どれくらい不安を感じやすいか"
          onChange={(v) => setForm((prev) => ({ ...prev, trait_social_anxiety: v }))}
        />
        <SliderRow
          label="もともとの泣きやすさ"
          value={form.trait_crying_proneness}
          help="どんな場面でも涙が出やすいか"
          onChange={(v) => setForm((prev) => ({ ...prev, trait_crying_proneness: v }))}
        />
        <SliderRow
          label="感情を抑え込む傾向"
          value={form.trait_suppression}
          help="普段どれくらい感情表現を抑えるか"
          onChange={(v) => setForm((prev) => ({ ...prev, trait_suppression: v }))}
        />

        <button
          onClick={() => mutation.mutate(form)}
          disabled={mutation.isPending}
          className="w-full py-3 rounded-lg text-white font-semibold bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? "保存中..." : "設定を保存する"}
        </button>
      </div>
    </div>
  );
};
