import PropTypes from "prop-types";
import { Button } from "./Button";

/** States what happened + the next step, never vague or apologetic (§3.6, §5.1). */
export function ErrorState({ message, onRetry }) {
  return (
    <div role="alert" className="rounded-lg border border-grade-1/30 bg-grade-1/5 p-4 text-sm text-ink">
      <p>{message}</p>
      {onRetry ? (
        <div className="mt-2">
          <Button variant="secondary" onClick={onRetry}>
            Retry
          </Button>
        </div>
      ) : null}
    </div>
  );
}

ErrorState.propTypes = {
  message: PropTypes.string.isRequired,
  onRetry: PropTypes.func,
};
