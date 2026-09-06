import PropTypes from "prop-types";
import { useEffect, useRef } from "react";

/** Slides in from the right — used for the collapsed-nav drawer under `md` (§3.5). */
export function Drawer({ title, isOpen, onClose, children }) {
  const panelRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;
    panelRef.current?.focus();

    function handleKeyDown(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-ink/40" onClick={onClose}>
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        tabIndex={-1}
        onClick={(event) => event.stopPropagation()}
        className="absolute inset-y-0 right-0 w-72 bg-surface-raised p-4 shadow-lg
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
      >
        <h2 id="drawer-title" className="text-lg font-semibold text-ink">
          {title}
        </h2>
        <div className="mt-3 text-sm text-ink">{children}</div>
      </div>
    </div>
  );
}

Drawer.propTypes = {
  title: PropTypes.string.isRequired,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
};
