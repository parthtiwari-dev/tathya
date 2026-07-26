// Deterministic, muted accent color derived from a label (ministry name, or
// the anchor entity name when there's no ministry). Same label always
// produces the same hue, so a given ministry/person reads as a consistent
// color across every card and every visit -- a lightweight visual "desk"
// system without needing real topic imagery. Kept desaturated/mid-lightness
// so it works as a subtle tint on both the light and dark paper backgrounds
// rather than competing with them.

export function accentColorFromLabel(label: string): string {
  let hash = 0;
  for (let i = 0; i < label.length; i++) {
    hash = label.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 32% 46%)`;
}
