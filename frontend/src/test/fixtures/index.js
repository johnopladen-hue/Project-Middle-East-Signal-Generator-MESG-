/**
 * Captured API responses - NOT hand-written. Produced by
 * `python scripts/capture_frontend_fixtures.py` running the real UCDP/OFAC
 * harvesters over the genuine excerpts in backend/tests/fixtures/ and calling
 * the real endpoints ("harvest, never generate", D-012/D-013). Stories in
 * geo_items_centcom.json come from the repo's own labelled synthetic seed
 * (app.dev_seed, "[SYNTHETIC — DEV SEED]"). geo_items_news.json and the raw_item_detail_*
 * files come from the genuine t.me fixture pages run through the real Telegram
 * collector and gazetteer (D-023).
 *
 * Look records up by name via these helpers rather than hard-coding ids -
 * ids are autoincrement and can shift on re-capture.
 */
import capabilities from "./capabilities.json";
import geoItemsCentcom from "./geo_items_centcom.json";
import geoItemsNews from "./geo_items_news.json";
import organizationDetails from "./organization_details.json";
import organizations from "./organizations.json";
import pipelineStatus from "./pipeline_status.json";
import rawItemDetailLocated from "./raw_item_detail_located.json";
import rawItemDetailUnlocated from "./raw_item_detail_unlocated.json";
import regions from "./regions.json";

export {
  capabilities,
  geoItemsCentcom,
  geoItemsNews,
  organizationDetails,
  organizations,
  pipelineStatus,
  rawItemDetailLocated,
  rawItemDetailUnlocated,
  regions,
};

export function orgSummaryByName(name) {
  const org = organizations.find((o) => o.name === name);
  if (!org) throw new Error(`No captured organization named ${name}`);
  return org;
}

export function orgDetailByName(name) {
  const detail = Object.values(organizationDetails).find((o) => o.name === name);
  if (!detail) throw new Error(`No captured organization profile named ${name}`);
  return detail;
}
