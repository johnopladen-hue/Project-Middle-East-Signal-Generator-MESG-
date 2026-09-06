import PropTypes from "prop-types";
import { Card } from "../components/primitives/Card";

/** The design centerpiece (UI-spec §3.5) — the product's reason to exist. */
export function DivergencePanel({ divergence }) {
  return (
    <div className="grid grid-cols-1 gap-0 overflow-hidden rounded-lg border border-rule sm:grid-cols-2">
      <Card className="rounded-none border-0 border-b border-rule sm:border-b-0 sm:border-r">
        <h3 className="mb-2 text-xs font-semibold uppercase text-ink-muted">In-region voices</h3>
        <p className="reading-measure text-sm text-ink">{divergence.in_region_summary}</p>
      </Card>
      <Card className="rounded-none border-0">
        <h3 className="mb-2 text-xs font-semibold uppercase text-ink-muted">English-language media</h3>
        <p className="reading-measure text-sm text-ink">{divergence.english_media_summary}</p>
      </Card>
      <div className="col-span-full space-y-2 border-t border-rule bg-surface p-4">
        <p className="text-xs">
          <span className="font-semibold text-ink">Diverges on: </span>
          <span className="text-ink-muted">
            {divergence.divergence_points.length > 0 ? divergence.divergence_points.join(" · ") : "None noted."}
          </span>
        </p>
        <p className="text-xs">
          <span className="font-semibold text-ink">Converges on: </span>
          <span className="text-ink-muted">
            {divergence.convergence_points.length > 0 ? divergence.convergence_points.join(" · ") : "None noted."}
          </span>
        </p>
      </div>
    </div>
  );
}

DivergencePanel.propTypes = {
  divergence: PropTypes.shape({
    in_region_summary: PropTypes.string.isRequired,
    english_media_summary: PropTypes.string.isRequired,
    divergence_points: PropTypes.arrayOf(PropTypes.string).isRequired,
    convergence_points: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
};
