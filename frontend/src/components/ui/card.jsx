import React from "react";

export default function Card({ title, subtitle, actions, className = "", children }) {
  return (
    <section
      className={`rounded-2xl bg-white shadow-sm border border-slate-200 ${className}`}
    >
      {(title || subtitle || actions) && (
        <header className="flex items-start justify-between gap-3 px-5 pt-5">
          <div>
            {title && (
              <h3 className="text-slate-900 font-semibold leading-6">{title}</h3>
            )}
            {subtitle && (
              <p className="text-slate-500 text-sm mt-0.5">{subtitle}</p>
            )}
          </div>
          {actions}
        </header>
      )}
      <div className={`${title || subtitle ? "px-5 pb-5 pt-3" : "p-5"}`}>
        {children}
      </div>
    </section>
  );
}