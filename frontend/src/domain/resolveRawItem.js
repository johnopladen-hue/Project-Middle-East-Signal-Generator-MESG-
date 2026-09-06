/** Maps a content_json raw-item entry (snake_case, TDD §6 field names) to
 * the RawItem shape RawItemView/ProvenanceChip expect. */
export function resolveRawItem(raw) {
  return {
    id: raw.id,
    sourceName: raw.source_name,
    accessLevel: raw.access_level,
    url: raw.url,
    fetchedAt: raw.fetched_at,
    originalLang: raw.original_lang,
    contentHash: raw.content_hash,
    originalText: raw.original_text,
    workingText: raw.working_text,
  };
}
