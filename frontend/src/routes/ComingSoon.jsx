import PropTypes from "prop-types";

/** Placeholder for a route not yet built by its order in the UI-spec sequence. */
export function ComingSoon({ title }) {
  return (
    <div className="p-8">
      <h1 className="text-xl font-semibold text-ink">{title}</h1>
      <p className="mt-2 text-sm text-ink-muted">Not built yet — lands in a later order.</p>
    </div>
  );
}

ComingSoon.propTypes = {
  title: PropTypes.string.isRequired,
};
