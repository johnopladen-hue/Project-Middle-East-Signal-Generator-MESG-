import PropTypes from "prop-types";

/** A labeled chip, e.g. for event type. Plain text on a quiet background — no color-only meaning. */
export function Tag({ children }) {
  return (
    <span className="inline-flex items-center rounded border border-rule px-2 py-0.5 text-xs text-ink-muted">
      {children}
    </span>
  );
}

Tag.propTypes = {
  children: PropTypes.node.isRequired,
};
