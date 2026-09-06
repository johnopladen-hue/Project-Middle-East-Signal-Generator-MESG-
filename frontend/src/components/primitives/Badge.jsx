import PropTypes from "prop-types";

const TONE_CLASSES = {
  neutral: "bg-accent-weak text-accent",
  "grade-5": "bg-grade-5/15 text-grade-5",
  "grade-4": "bg-grade-4/15 text-grade-4",
  "grade-3": "bg-grade-3/15 text-grade-3",
  "grade-2": "bg-grade-2/15 text-grade-2",
  "grade-1": "bg-grade-1/15 text-grade-1",
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
