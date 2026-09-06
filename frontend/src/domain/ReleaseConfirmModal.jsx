import PropTypes from "prop-types";
import { Button } from "../components/primitives/Button";
import { Modal } from "../components/primitives/Modal";
import { Skeleton } from "../components/primitives/Skeleton";

/** States the blast radius before anything sends (UI-spec §5.3):
 * "This sends to N active recipients (E email, S SMS). This cannot be
 * recalled." No call fires until this is explicitly confirmed. */
export function ReleaseConfirmModal({ isOpen, onClose, onConfirm, summary, isLoadingSummary, isReleasing }) {
  return (
    <Modal title="Release to recipients" isOpen={isOpen} onClose={onClose}>
      {isLoadingSummary || !summary ? (
        <Skeleton lines={2} />
      ) : (
        <p>
          This sends to {summary.active_count} active recipients ({summary.email_count} email,{" "}
          {summary.sms_count} SMS). This cannot be recalled.
        </p>
      )}
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="secondary" onClick={onClose} disabled={isReleasing}>
          Cancel
        </Button>
        <Button onClick={onConfirm} busy={isReleasing} disabled={isLoadingSummary || !summary}>
          Release to recipients
        </Button>
      </div>
    </Modal>
  );
}

ReleaseConfirmModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  summary: PropTypes.shape({
    active_count: PropTypes.number.isRequired,
    email_count: PropTypes.number.isRequired,
    sms_count: PropTypes.number.isRequired,
  }),
  isLoadingSummary: PropTypes.bool,
  isReleasing: PropTypes.bool,
};
