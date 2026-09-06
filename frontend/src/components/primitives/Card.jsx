import PropTypes from "prop-types";

/** Cards use rules and spacing, not a soft-grey drop-shadow (§3.1). */
export function Card({ children, className = "" }) {
  return (
    <div className={`rounded-lg border border-rule bg-surface-raised p-4 ${className}`}>
      {children}
    </div>
  );
}

Card.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};
