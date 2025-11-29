import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/api/client";
import { CausalEffectForestChart, EffectDatum } from "@/features/emotion/components/CausalEffectForestChart";
import { EmotionTimelineChart, TimelinePoint } from "@/features/emotion/components/EmotionTimelineChart";
import { EffectSummaryCards, SummaryStats } from "@/features/emotion/components/EffectSummaryCards";
import { EvalToCryingPathCard, PathSummary } from "@/features/emotion/components/EvalToCryingPathCard";

type EffectsResponse = {
  effects: EffectDatum[];
};

type TimelineResponse = {
  points: TimelinePoint[];
};

export const EmotionDashboardPage: React.FC = () => {
  const summaryQuery = useQuery({
    queryKey: ["emotion", "dashboard", "summary"],
    queryFn: () => apiFetch<SummaryStats>("/api/emotion/dashboard/summary"),
  });

  const effectsQuery = useQuery({
    queryKey: ["emotion", "effects"],
    queryFn: () => apiFetch<EffectsResponse>("/api/emotion/effects/me"),
  });

  const timelineQuery = useQuery({
    queryKey: ["emotion", "timeline"],
    queryFn: () => apiFetch<TimelineResponse>("/api/emotion/episodes/timeline/me"),
  });

  const pathSummaryQuery = useQuery({
    queryKey: ["emotion", "path-summary"],
    queryFn: async () => {
      try {
        return await apiFetch<PathSummary>("/api/emotion/path-summary/me");
      } catch (error) {
        const err = error as Error & { status?: number };
        if (err.status === 404) {
          return null;
        }
        throw err;
      }
    },
  });

  if (summaryQuery.isLoading || effectsQuery.isLoading || timelineQuery.isLoading || pathSummaryQuery.isLoading) {
    return <div className="text-gray-500">読み込み中...</div>;
  }

  if (summaryQuery.isError || effectsQuery.isError || timelineQuery.isError || pathSummaryQuery.isError) {
    return <div className="text-red-500 text-sm">データの取得に失敗しました。</div>;
  }

  const effects = effectsQuery.data?.effects ?? [];
  const timeline = timelineQuery.data?.points ?? [];
  const summary = summaryQuery.data as SummaryStats;
  const pathSummary = pathSummaryQuery.data ?? undefined;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">あなたのパターン</h1>
        <p className="text-sm text-gray-500">因果推定の結果と時系列を一つの画面で振り返れます。</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EvalToCryingPathCard data={pathSummary ?? undefined} />
        <EffectSummaryCards summary={summary} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CausalEffectForestChart data={effects} outcomeName="crying_level" />
        <CausalEffectForestChart data={effects} outcomeName="expression_score" />
        <CausalEffectForestChart data={effects} outcomeName="stress_after" />
        <CausalEffectForestChart data={effects} outcomeName="relationship_impact" />
      </div>
      <EmotionTimelineChart data={timeline} />
    </div>
  );
};
