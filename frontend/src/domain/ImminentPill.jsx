import { Zap } from "lucide-react";

/** Distinct from SeverityMark — a low-severity imminent signal and a
 * high-severity confirmed one are different objects (UI-spec §3.3). */
export function ImminentPill() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-grade-2/15 px-2 py-0.5 text-xs font-medium text-grade-2">
      <Zap size={12} aria-hidden="true" />
      Imminent
    </span>
  );
}
