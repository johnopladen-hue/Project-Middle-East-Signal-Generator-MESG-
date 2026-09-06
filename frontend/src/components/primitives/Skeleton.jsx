import PropTypes from "prop-types";

/** Loading placeholder — every data view uses this for its loading state (§5.1), never a spinner alone. */
export function Skeleton({ lines = 3 }) {
  return (
    <div role="status" aria-label="Loading" className="animate-pulse space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="h-4 rounded bg-rule" style={{ width: `${100 - index * 15}%` }} />
      ))}
    </div>
  );
}

Skeleton.propTypes = {
  lines: PropTypes.number,
};
