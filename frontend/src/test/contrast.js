/** WCAG 2.x relative-luminance / contrast-ratio math, used by the
 * accessibility regression test (Order 11 PROOF: "contrast checks pass"). */

function srgbChannel(c) {
  const normalized = c / 255;
  return normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
}

export function relativeLuminance([r, g, b]) {
  const [rl, gl, bl] = [srgbChannel(r), srgbChannel(g), srgbChannel(b)];
  return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl;
}

export function contrastRatio(rgbA, rgbB) {
  const lA = relativeLuminance(rgbA);
  const lB = relativeLuminance(rgbB);
  const lighter = Math.max(lA, lB);
  const darker = Math.min(lA, lB);
  return (lighter + 0.05) / (darker + 0.05);
}

/** Blends a foreground color over a background at the given alpha (0-1) —
 * models a Tailwind `/N` opacity utility (e.g. bg-grade-3/15) composited
 * onto its actual page background, since that's what a viewer's eye
 * actually reads contrast against, not the swatch color alone. */
export function blend(fgRgb, bgRgb, alpha) {
  return fgRgb.map((channel, index) => channel * alpha + bgRgb[index] * (1 - alpha));
}

export const WCAG_AA_NORMAL_TEXT = 4.5;
