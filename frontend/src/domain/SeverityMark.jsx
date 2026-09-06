import { AlertOctagon, AlertTriangle, Info, TriangleAlert } from "lucide-react";
import PropTypes from "prop-types";

/** Left-rule + labeled icon — never a color fill (UI-spec §3.3). Kept
 * visually distinct from GradeBlock: severity and truth grade are
 * different axes and must never be confused. */
const SEVERITY_CONFIG = {
  critical: { label: "Critical", icon: AlertOctagon, borderClass: "border-l-4 border-grade-1" },
  high: { label: "High", icon: AlertTriangle, borderClass: "border-l-4 border-grade-2" },
  elevated: { label: "Elevated", icon: TriangleAlert, borderClass: "border-l-2 border-grade-3" },
  info: { label: "Info", icon: Info, borderClass: "border-l-2 border-rule" },
};

export function SeverityMark({ severity }) {
  const config = SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.info;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1 pl-2 text-xs text-ink-muted ${config.borderClass}`}>
      <Icon size={14} aria-hidden="true" />
      {config.label}
    </span>
  );
}

SeverityMark.propTypes = {
  severity: PropTypes.oneOf(["critical", "high", "elevated", "info"]).isRequired,
};
