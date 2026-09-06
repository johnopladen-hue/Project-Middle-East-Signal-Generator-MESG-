/**
 * View-model shapes the UI consumes, mirroring TDD §6 field-for-field.
 * F-1 mitigation for no-TypeScript: these typedefs plus PropTypes on every
 * component are how analytic shapes stay documented and checkable at
 * runtime. The API client (src/api) normalizes raw responses to these
 * shapes at the boundary — no component reads a raw API shape directly.
 *
 * @typedef {Object} User
 * @property {number} id
 * @property {string} username
 * @property {"admin"|"viewer"} role
 * @property {boolean} active
 *
 * @typedef {Object} RawItem
 * @property {number} id
 * @property {number} sourceId
 * @property {string} fetchedAt - ISO timestamp
 * @property {string} originalLang
 * @property {string} originalText
 * @property {string|null} workingText
 * @property {string} url
 * @property {string} contentHash
 *
 * @typedef {Object} Fact
 * @property {string} text
 * @property {number[]} rawItemIds - empty means unverified
 * @property {boolean} unverified
 *
 * @typedef {Object} SourceAssessment
 * @property {number} sourceId
 * @property {string} sourceName
 * @property {"direct"|"one_step"|"aggregator"|"commentary"} accessLevel
 * @property {number} reliability
 * @property {string} rationale
 *
 * @typedef {Object} Divergence
 * @property {string} inRegionSummary
 * @property {string} englishMediaSummary
 * @property {string[]} divergencePoints
 * @property {string[]} convergencePoints
 *
 * @typedef {Object} Analysis
 * @property {number} id
 * @property {Fact[]} facts
 * @property {string} analysisText
 * @property {number} probabilityGrade - 1-5
 * @property {string|null} contraryEvidence
 * @property {boolean} hasCorroboratingArtefact
 *
 * @typedef {Object} Story
 * @property {number} id
 * @property {string} title
 * @property {string|null} eventType
 * @property {string} status
 * @property {Analysis} analysis
 * @property {SourceAssessment[]} sourceAssessments
 * @property {Divergence|null} divergence
 *
 * @typedef {Object} Signal
 * @property {number} id
 * @property {number} storyId
 * @property {string} type
 * @property {"critical"|"high"|"elevated"|"info"} severity
 * @property {boolean} isImminent
 * @property {"new"|"reviewed"|"released"|"suppressed"} status
 * @property {number} probabilityGrade
 * @property {string} createdAt
 *
 * @typedef {Object} Brief
 * @property {number} id
 * @property {"daily"|"weekly"} type
 * @property {string} forDate
 * @property {Object} content
 * @property {string|null} releasedAt
 *
 * @typedef {Object} Recipient
 * @property {number} id
 * @property {string} name
 * @property {string|null} email
 * @property {string|null} phone
 * @property {string[]} channels
 * @property {boolean} active
 * @property {string|null} approvedBy
 *
 * @typedef {Object} Source
 * @property {number} id
 * @property {string} name
 * @property {string} url
 * @property {string} language
 * @property {string|null} dialect
 * @property {string} type
 * @property {string|null} region
 * @property {number} credibilityPrior
 * @property {string|null} lastSeenAt
 * @property {boolean} active
 */

export {};
