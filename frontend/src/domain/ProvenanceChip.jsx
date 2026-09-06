import PropTypes from "prop-types";
import { useState } from "react";
import { Modal } from "../components/primitives/Modal";
import { RawItemView } from "./RawItemView";

const ACCESS_LABELS = {
  direct: "direct",
  one_step: "one-step",
  aggregator: "aggregator",
  commentary: "commentary",
};

/** A single source reference. Click reaches the raw item in one hop (TDD §8/§5.2). */
export function ProvenanceChip({ rawItem }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1 rounded border border-rule px-2 py-0.5 text-xs text-ink-muted
          hover:border-accent hover:text-accent
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        {rawItem.sourceName}
        <span className="text-ink-muted">· {ACCESS_LABELS[rawItem.accessLevel] ?? rawItem.accessLevel}</span>
      </button>
      <Modal title={rawItem.sourceName} isOpen={open} onClose={() => setOpen(false)}>
        <RawItemView rawItem={rawItem} />
      </Modal>
    </>
  );
}

ProvenanceChip.propTypes = {
  rawItem: PropTypes.shape({
    sourceName: PropTypes.string.isRequired,
    accessLevel: PropTypes.string,
  }).isRequired,
};
