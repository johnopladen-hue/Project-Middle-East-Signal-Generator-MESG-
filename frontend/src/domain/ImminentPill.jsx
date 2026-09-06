import { Zap } from "lucide-react";

/** Distinct from SeverityMark — a low-severity imminent signal and a
 * high-severity confirmed one are different objects (UI-spec §3.3).
 * Text is `ink`, not a grade color: text-grade-2 on bg-grade-2/15 measures
 * 3.35:1, failing WCAG AA (needs 4.5:1) — see Badge.jsx for the same
 * finding. The icon alone carries the color accent. */
export function ImminentPill() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-grade-2/15 px-2 py-0.5 text-xs font-medium text-ink">
      <Zap size={12} aria-hidden="true" className="text-grade-2" />
      Imminent
    </span>
  );
}
