// frontend/src/components/ExcellenceDashboard.jsx
import React, { useState } from "react";

/**
 * Prima Scholar – Excellence Dashboard
 * Minimal, self-contained component that compiles with CRA + Tailwind.
 * Replace placeholders with your real data / handlers when ready.
 */
export default function ExcellenceDashboard() {
  const [files, setFiles] = useState([]);
  const [query, setQuery] = useState("");

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <header className="px-6 py-4 border-b bg-white">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid place-items-center w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-500 text-white shadow-md">
              {/* Mark: open book + spark */}
              <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" aria-hidden="true">
                <path d="M5 7.5c2.5-1.8 5.3-1.8 8 0v9.2c-2.7-1.8-5.5-1.8-8 0V7.5Z" fill="white" opacity=".95"/>
                <path d="M11 7.5c2.7-1.8 5.5-1.8 8 0v9.2c-2.5-1.8-5.3-1.8-8 0V7.5Z" fill="white" opacity=".8"/>
                <path d="M12 3l.9 1.9 1.9.9-1.9.9L12 8.6l-.9-1.9-1.9-.9 1.9-.9L12 3Z" fill="#fde68a"/>
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900 leading-5">Prima Scholar</h1>
              <p className="text-slate-500 text-sm">Excellence Dashboard</p>
            </div>
          </div>

          <a
            href="#"
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 text-white px-3 py-2 text-sm hover:bg-slate-800 transition"
            title="Project Docs"
          >
            <span>Docs</span>
            <svg viewBox="0 0 20 20" className="w-4 h-4" fill="currentColor" aria-hidden="true">
              <path d="M12.293 2.293a1 1 0 0 1 1.414 0l4 4A1 1 0 0 1 17 8h-3a2 2 0 0 1-2-2V3a1 1 0 0 1 .293-.707Z"/>
              <path d="M11 3H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V9h-3a2 2 0 0 1-2-2V3Z"/>
            </svg>
          </a>
        </div>
      </header>

      {/* Content */}
      <main className="px-6 py-6">
        <div className="mx-auto max-w-7xl grid gap-6 lg:grid-cols-3">
          {/* Search / quick actions */}
          <section className="lg:col-span-2 rounded-2xl bg-white p-5 shadow-sm border">
            <h2 className="font-semibold text-slate-800">Quick Search</h2>
            <p className="text-slate-500 text-sm mb-3">
              Look up papers, notes, or summaries you’ve worked on.
            </p>
            <div className="flex gap-3">
              <input
                className="w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-sky-500"
                placeholder="Search by title, keyword, or author…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="button"
                className="rounded-xl bg-sky-600 text-white px-4 py-2 font-medium hover:bg-sky-500 transition"
                onClick={() => alert(`Search queued: ${query || "empty query"}`)}
              >
                Search
              </button>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {["Upload PDF", "New Note", "Summarize", "Cite"].map((label) => (
                <button
                  key={label}
                  className="rounded-full border px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
                  type="button"
                  onClick={() => alert(`${label} clicked`)}
                >
                  {label}
                </button>
              ))}
            </div>
          </section>

          {/* Status / metrics */}
          <aside className="rounded-2xl bg-white p-5 shadow-sm border">
            <h2 className="font-semibold text-slate-800">Workspace Status</h2>
            <ul className="mt-3 space-y-3">
              <li className="flex items-center justify-between">
                <span className="text-slate-600">Documents indexed</span>
                <span className="font-semibold text-slate-900">—</span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-slate-600">Pending summaries</span>
                <span className="font-semibold text-slate-900">—</span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-slate-600">Redis cache</span>
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 text-emerald-700 px-2 py-0.5 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> OK
                </span>
              </li>
            </ul>
          </aside>

          {/* Upload area */}
          <section className="lg:col-span-3 rounded-2xl bg-white p-5 shadow-sm border">
            <h2 className="font-semibold text-slate-800">Upload Documents</h2>
            <p className="text-slate-500 text-sm mb-3">
              Drop your PDFs or TXT files here to be processed and summarized.
            </p>
            <label
              className="flex flex-col items-center justify-center gap-2 border-2 border-dashed rounded-2xl py-10 cursor-pointer hover:bg-slate-50"
              style={{ borderColor: "#cbd5e1" }}
            >
              <svg viewBox="0 0 24 24" className="w-8 h-8 text-slate-500" fill="none" aria-hidden="true">
                <path d="M12 16V4m0 0 4 4m-4-4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <rect x="4" y="14" width="16" height="6" rx="2" stroke="currentColor" strokeWidth="2"/>
              </svg>
              <span className="text-slate-700 font-medium">Choose files or drag & drop</span>
              <span className="text-slate-500 text-xs">PDF, TXT • up to 50MB</span>
              <input
                type="file"
                className="hidden"
                multiple
                accept=".pdf,.txt"
                onChange={(e) => setFiles(Array.from(e.target.files || []))}
              />
            </label>

            {files.length > 0 && (
              <div className="mt-4 rounded-xl border bg-slate-50 p-3">
                <p className="text-sm text-slate-600 mb-2">
                  Selected <strong>{files.length}</strong> file{files.length > 1 ? "s" : ""}:
                </p>
                <ul className="text-sm text-slate-700 list-disc pl-5">
                  {files.map((f) => (
                    <li key={f.name}>{f.name}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </div>
      </main>

      <footer className="px-6 py-8">
        <div className="mx-auto max-w-7xl text-center text-slate-400 text-sm">
          © {new Date().getFullYear()} Prima Scholar. All rights reserved.
        </div>
      </footer>
    </div>
  );
}