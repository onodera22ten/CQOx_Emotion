import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";

export type TimelinePoint = {
  episode_id: number;
  label: string;
  crying_level: number;
  expression_score: number;
  relationship_impact: number;
};

type Props = {
  data: TimelinePoint[];
};

export const EmotionTimelineChart: React.FC<Props> = ({ data }) => {
  if (data.length === 0) {
    return (
      <div className="p-4 border rounded-2xl bg-white shadow-sm">
        <h3 className="text-sm font-semibold mb-2">エピソードごとの推移</h3>
        <p className="text-sm text-gray-500">まだ記録されたエピソードがありません。</p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-2xl bg-white shadow-sm">
      <h3 className="text-sm font-semibold mb-2">エピソードごとの推移</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <XAxis dataKey="label" angle={-45} textAnchor="end" height={60} fontSize={12} />
            <YAxis />
            <Tooltip />
            <Legend />
            <ReferenceLine y={0} strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="crying_level"
              name="涙レベル"
              stroke="#ec4899"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="expression_score"
              name="伝えられた感"
              stroke="#3b82f6"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="relationship_impact"
              name="関係への影響"
              stroke="#10b981"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
