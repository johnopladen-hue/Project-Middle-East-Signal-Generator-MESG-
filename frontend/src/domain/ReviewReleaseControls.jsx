import PropTypes from "prop-types";
import { useState } from "react";
import { useAuth } from "../app/AuthContext";
import { Button } from "../components/primitives/Button";
import { useToast } from "../components/primitives/Toast";
import { ReleaseConfirmModal } from "./ReleaseConfirmModal";
import { useRecipientsSummary, useReleaseSignal, useSuppressSignal } from "./useSignals";

/** Admin-only (F-7); client-side hiding is defense-in-depth, the server
 * is the real gate (403 on /signals/:id/release|suppress for non-admins). */
export function ReviewReleaseControls({ signalId }) {
  const { user } = useAuth();
  const [releaseModalOpen, setReleaseModalOpen] = useState(false);
  const [confirmingSuppress, setConfirmingSuppress] = useState(false);
  const showToast = useToast();

  const summaryQuery = useRecipientsSummary(releaseModalOpen);
  const releaseMutation = useReleaseSignal(signalId);
  const suppressMutation = useSuppressSignal(signalId);

  if (user?.role !== "admin") return null;

  async function handleConfirmRelease() {
    await releaseMutation.mutateAsync();
    setReleaseModalOpen(false);
    showToast("Released.");
  }

  async function handleConfirmSuppress() {
    await suppressMutation.mutateAsync();
    setConfirmingSuppress(false);
    showToast("Suppressed.");
  }

  return (
    <div className="flex items-center gap-2">
      <Button onClick={() => setReleaseModalOpen(true)}>Release to recipients</Button>

      {confirmingSuppress ? (
        <span className="flex items-center gap-2 text-sm text-ink">
          Suppress this signal?
          <Button variant="danger" busy={suppressMutation.isPending} onClick={handleConfirmSuppress}>
            Yes
          </Button>
          <Button variant="secondary" onClick={() => setConfirmingSuppress(false)}>
            No
          </Button>
        </span>
      ) : (
        <Button variant="secondary" onClick={() => setConfirmingSuppress(true)}>
          Suppress
        </Button>
      )}

      <ReleaseConfirmModal
        isOpen={releaseModalOpen}
        onClose={() => setReleaseModalOpen(false)}
        onConfirm={handleConfirmRelease}
        summary={summaryQuery.data}
        isLoadingSummary={summaryQuery.isLoading}
        isReleasing={releaseMutation.isPending}
      />
    </div>
  );
}

ReviewReleaseControls.propTypes = {
  signalId: PropTypes.number.isRequired,
};
