import PropTypes from "prop-types";

/** Icon-only button. `label` is mandatory — it becomes the accessible name (§5.5). */
export function IconButton({ label, icon: Icon, ...rest }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className="inline-flex items-center justify-center rounded-md p-2 text-ink-muted
        hover:bg-accent-weak hover:text-accent
        focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      {...rest}
    >
      <Icon size={18} aria-hidden="true" />
    </button>
  );
}

IconButton.propTypes = {
  label: PropTypes.string.isRequired,
  icon: PropTypes.elementType.isRequired,
};
