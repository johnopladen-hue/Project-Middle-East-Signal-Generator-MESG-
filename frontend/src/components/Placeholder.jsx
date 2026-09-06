import PropTypes from "prop-types";

/** Order 1 scaffold proof component — replaced by real primitives in Order 2. */
export function Placeholder({ label }) {
  return <p>{label}</p>;
}

Placeholder.propTypes = {
  label: PropTypes.string.isRequired,
};
