import PropTypes from "prop-types";

/** Grade tones use `text-ink` (not text-grade-N) on a light grade-N tint.
 * Measured contrast (UI-Spec-and-Claude-Code-Orders-v0.1.md §5.5, WCAG AA,
 * 4.5:1 minimum): text-grade-N on bg-grade-N/15 fails for grade 2/3/4
 * (2.4-3.4:1) and is borderline for grade 5 (4.3:1) — the mid palette
 * hues (UI-spec §3.2) are too light/mid-luminance as text color at any
 * usable tint or solid strength. Text stays `ink` (always ~15:1+ on these
 * light tints); the grade hue still reinforces via the background tint,
 * consistent with "numeral is the primary signal, color reinforces" —
 * color was never meant to be the sole carrier anyway. */
const TONE_CLASSES = {
  neutral: "bg-accent-weak text-accent",
  "grade-5": "bg-grade-5/15 text-ink",
  "grade-4": "bg-grade-4/15 text-ink",
  "grade-3": "bg-grade-3/15 text-ink",
  "grade-2": "bg-grade-2/15 text-ink",
  "grade-1": "bg-grade-1/15 text-ink",
};

/** A small pill for counts/labels. Always carries text, never color alone (§3.2/§5.5). */
export function Badge({ tone = "neutral", children }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}
    >
      {children}
    </span>
  );
}

Badge.propTypes = {
  tone: PropTypes.oneOf(["neutral", "grade-5", "grade-4", "grade-3", "grade-2", "grade-1"]),
  children: PropTypes.node.isRequired,
};
