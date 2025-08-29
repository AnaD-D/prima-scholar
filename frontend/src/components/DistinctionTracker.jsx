import React from "react";
import Card from "./ui/card";

const ACHIEVEMENTS = [
  { name: "Top 5% GPA", progress: 80 },
  { name: "Published Abstract", progress: 60 },
  { name: "Conference Talk", progress: 35 },
];

export default function DistinctionTracker() {
  return (
    <Card title="Distinction Tracker" subtitle="Keep an eye on academic milestones.">
      <ul className="space-y-4">
        {ACHIEVEMENTS.map((a) => (
          <li key={a.name}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-slate-700">{a.name}</span>
              <span className="text-xs text-slate-500">{a.progress}%</span>
            </div>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-sky-500"
                style={{ width: `${a.progress}%` }}
                aria-hidden="true"
              />
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
