import React from "react";
import Card from "./ui/card";
import Button from "./ui/button";

const DEMO = [
  { mentor: "Dr. Elaine Rivers", topic: "Neural IR", next: "Mon 10:30", status: "active" },
  { mentor: "Prof. Mateo Vargas", topic: "Prompt Engineering", next: "Wed 14:00", status: "active" },
  { mentor: "Dr. Hana Kim", topic: "Academic Writing", next: "Fri 09:00", status: "paused" },
];

export default function ScholarMentorship() {
  return (
    <Card
      title="Scholar Mentorship"
      subtitle="Your active mentoring sessions and topics."
      actions={<Button variant="primary">New Session</Button>}
    >
      <ul className="divide-y divide-slate-200">
        {DEMO.map((m) => (
          <li key={m.mentor} className="py-3 flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-900">{m.mentor}</p>
              <p className="text-slate-500 text-sm">{m.topic}</p>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  m.status === "active"
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {m.status}
              </span>
              <span className="text-slate-500 text-sm">Next: {m.next}</span>
              <Button variant="outline" size="sm">
                Join
              </Button>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}