import PropTypes from "prop-types";

/** Directive copy, never a bare "No data" (§3.6, §5.1). */
export function EmptyState({ message, action }) {
  return (
    <div className="rounded-lg border border-dashed border-rule p-8 text-center">
      <p className="text-sm text-ink-muted">{message}</p>
      {action ? <div className="mt-3">{action}</div> : null}
    </div>
  );
}

EmptyState.propTypes = {
  message: PropTypes.string.isRequired,
  action: PropTypes.node,
};
