import PropTypes from "prop-types";

const VARIANT_CLASSES = {
  primary: "bg-accent text-white hover:opacity-90",
  secondary: "bg-surface-raised text-ink border border-rule hover:bg-accent-weak",
  danger: "bg-grade-1 text-white hover:opacity-90",
};

export function Button({ variant = "primary", busy = false, disabled = false, children, ...rest }) {
  return (
    <button
      type="button"
      disabled={disabled || busy}
      aria-busy={busy}
      className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium
        transition-opacity disabled:cursor-not-allowed disabled:opacity-50
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
        ${VARIANT_CLASSES[variant]}`}
      {...rest}
    >
      {busy ? "Working…" : children}
    </button>
  );
}

Button.propTypes = {
  variant: PropTypes.oneOf(["primary", "secondary", "danger"]),
  busy: PropTypes.bool,
  disabled: PropTypes.bool,
  children: PropTypes.node.isRequired,
};
