import React from "react";
import Card from "./ui/card";
import Button from "./ui/button";

const RESOURCES = [
  { title: "Graduate Application Checklist", href: "#", tag: "guide" },
  { title: "Research Statement Examples", href: "#", tag: "templates" },
  { title: "Scholarship Opportunities (STEM)", href: "#", tag: "funding" },
];

export default function EliteResources() {
  return (
    <Card title="Elite Resources" subtitle="Curated tools and references for high achievers.">
      <ul className="space-y-3">
        {RESOURCES.map((r) => (
          <li
            key={r.title}
            className="flex items-center justify-between gap-3 border border-slate-200 rounded-xl px-4 py-3"
          >
            <div>
              <p className="font-medium text-slate-900">{r.title}</p>
              <span className="text-xs text-slate-500">#{r.tag}</span>
            </div>
            <Button as="a" href={r.href} variant="outline" size="sm">
              Open
            </Button>
          </li>
        ))}
      </ul>
    </Card>
  );
}