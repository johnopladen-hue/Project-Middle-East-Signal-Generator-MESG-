import PropTypes from "prop-types";
import { useId } from "react";

export function FormField({ label, error, type = "text", ...inputProps }) {
  const id = useId();
  const errorId = `${id}-error`;

  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-ink">
        {label}
      </label>
      <input
        id={id}
        type={type}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        className={`mt-1 w-full rounded-md border px-3 py-2 text-sm
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
          ${error ? "border-grade-1" : "border-rule"}`}
        {...inputProps}
      />
      {error ? (
        <p id={errorId} className="mt-1 text-xs text-grade-1">
          {error}
        </p>
      ) : null}
    </div>
  );
}

FormField.propTypes = {
  label: PropTypes.string.isRequired,
  error: PropTypes.string,
  type: PropTypes.string,
};
