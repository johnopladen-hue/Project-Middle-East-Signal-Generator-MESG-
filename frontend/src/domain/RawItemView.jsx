import PropTypes from "prop-types";

/** Original + translation side by side, with the fetch artefact (TDD §4.1/§4.2/§8). */
export function RawItemView({ rawItem }) {
  return (
    <div>
      <dl className="mb-4 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs text-ink-muted">
        <dt>Source</dt>
        <dd>{rawItem.sourceName}</dd>
        <dt>URL</dt>
        <dd className="truncate">{rawItem.url}</dd>
        <dt>Fetched</dt>
        <dd>{rawItem.fetchedAt}</dd>
        <dt>Original language</dt>
        <dd>{rawItem.originalLang}</dd>
        <dt>Content hash</dt>
        <dd className="truncate">{rawItem.contentHash}</dd>
      </dl>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase text-ink-muted">
            Original ({rawItem.originalLang})
          </h3>
          <p className="reading-measure text-sm text-ink" dir="auto">
            {rawItem.originalText}
          </p>
        </div>
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase text-ink-muted">Translation</h3>
          <p className="reading-measure text-sm text-ink">
            {rawItem.workingText ?? "Not yet translated."}
          </p>
        </div>
      </div>
    </div>
  );
}

RawItemView.propTypes = {
  rawItem: PropTypes.shape({
    sourceName: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
    fetchedAt: PropTypes.string.isRequired,
    originalLang: PropTypes.string.isRequired,
    contentHash: PropTypes.string.isRequired,
    originalText: PropTypes.string.isRequired,
    workingText: PropTypes.string,
  }).isRequired,
};
