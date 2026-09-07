# Material research for a paper-like interactive site

Research date: 2026-09-07

This note separates what the sources document from suggested digital adaptations.

## Primary-source references and observations

### 1. Degas and layered tracing paper — The Metropolitan Museum of Art

Source: [A Disputed Pastel Reclaimed for Degas (Metropolitan Museum Journal)](https://resources.metmuseum.org/resources/metpublications/pdf/Metropolitan_Museum_Journal_v_51_2016.pdf)

**Observed:** The Met describes Edgar Degas pinning tracing paper over an existing drawing, copying a motif onto the new sheet, then repeating the process while altering outlines. Tracing paper served both as a copying device and as the physical/aesthetic basis of a layered composition. The material is translucent, smooth, and technically difficult for loosely bound charcoal and pastel.

**Adaptation:** Build a “trace stack” in which each project layer is a separate absolutely positioned sheet. Let users toggle or drag layers, and preserve small registration offsets so the composite feels made through repeated copying rather than a perfectly aligned UI.

**Pitfall:** Tracing-paper translucency is not the same as simply lowering opacity: too many semi-transparent layers flatten contrast and make text illegible. Keep an opaque reading layer available and use texture sparingly.

### 2. Ryman’s tracing-paper collage — Museum of Modern Art

Source: [Robert Ryman catalogue, MoMA](https://www.moma.org/documents/moma_catalogue_405_300063098.pdf)

**Observed:** Ryman describes tracing paper as “very translucent and soft,” with elements standing out because of the material. The catalogue identifies a 1959 work made with pencil, casein, and tracing paper layered on tracing paper; the work relates materially to the wall behind it.

**Adaptation:** Treat the page background as an active substrate. Place a low-contrast “wall” field behind paper cards, with edges and joins visible; use translucency to let annotations appear as a composite rather than separate cards.

**Pitfall:** Soft translucent layers need a stable contrast anchor. Pair pale sheets with one dark registration line, caption, or tab per cluster.

### 3. Risograph color and overprint — RISO and SAIC Service Bureau

Sources: [RISO consumables / rice-bran-oil ink](https://www.riso.co.jp/english/product/digital_dup/consumables/index.html), [RISO Risograph creative printing](https://www.riso.co.uk/print-solutions/risograph-creative/), and [Everything Riso color/overlay guide (SAIC Service Bureau PDF)](https://sites.saic.edu/servicebureau/wp-content/uploads/sites/20/2025/03/EverythingRiso_2024.pdf)

**Observed:** RISO describes vegetable-based rice-bran-oil ink and a wide range of spot colors. The SAIC guide states that Risograph ink is translucent, that final appearance depends on paper color and layer order, and that overprinting creates new colors. RISO’s creative-printing page describes emulsion ink and outcomes that are unique from print to print.

**Adaptation:** Use a deliberately limited spot palette (for example, fluorescent pink, sunflower, blue, and black) and stack layers with `mix-blend-mode: multiply`. Add small x/y offsets and occasional clipped registration marks so a new color emerges where layers overlap.

**Pitfall:** CSS blending can look muddy on dark backgrounds and varies with compositing context. Keep the base paper light, test the exact stack in the target browser, and avoid depending on blend mode for essential text contrast.

### 4. Volvelles as a paper interface — New York Public Library

Source: [Round We Go: Volvelles at the Lionel Pincus and Princess Firyal Map Division](https://www.nypl.org/blog/2023/04/27/volvelles-lionel-pincus-princess-firyal-map-division)

**Observed:** NYPL defines a volvelle as a paper instrument made from one or more revolving discs marked with variables. Rotating discs work together to calculate or reveal information; examples include time, navigation, astronomy, and calendars. The physical artifacts are fragile and should not be freely rotated in the collection.

**Adaptation:** Make one interactive “dial” the site’s primary navigation: a circular index or wheel that changes the visible layer set, with labels aligned to a fixed reading window. A pointer, notch, or punched aperture can act as the affordance for the selected section.

**Pitfall:** A wheel is only useful if the mapping is legible. Include a static list or keyboard controls alongside pointer dragging, and keep the active state announced in text.

### 5. Movable books and overlays — New York Public Library

Source: [Movable books in the Spencer Collection](https://www.nypl.org/blog/2010/06/23/movable-books-spencer-collection)

**Observed:** NYPL describes movable books with flaps, pop-up pages, and overlays as a long-standing instructional form. A 1612 book by Jacopo Ligozzi and engravers Raffaello Schiaminossi and Domenico Falcini uses movable engraved overlays that let the reader “see inside” views. NYPL also describes paper engineering as a skilled construction practice.

**Adaptation:** Use flap-like cards for “before/after” or “inside” states: the closed state carries a diagram, and opening it reveals a second annotation layer beneath. In the browser, make the flap a real button with a transform-origin at its edge, while the revealed content remains in normal reading order for assistive technology.

**Pitfall:** A purely 3D flap can hide content from keyboard and screen-reader users. Keep the underlying information in the DOM and make motion decorative, with an explicit open/closed state.

## Browser implementation references

### Layer motion and compositing

- [MDN: `transform`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/transform) documents translate/rotate/scale/skew and warns that transforms create a stacking context. Use transforms for paper movement, but account for changed containing blocks when positioning descendants.
- [MDN: `mix-blend-mode`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/mix-blend-mode) documents blending an element with the backdrop in the same stacking context. `multiply` is the closest quick analogue to translucent ink overprint; isolate only where needed because stacking contexts change the blend result.
- [MDN: `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion) recommends detecting a user’s reduced-motion setting. Provide a reduced mode that removes large rotations/pans and keeps the final layer state visible; use opacity or an instant state change instead.

Minimal pattern:

```css
.sheet { transform: translate(var(--x), var(--y)) rotate(var(--r));
  mix-blend-mode: multiply; }
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: none; transform: none; }
}
```

### Same-origin cross-document transitions

- [MDN: Using the View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using) states that current and destination documents must be same-origin and both opt in with `@view-transition { navigation: auto; }`. The browser captures old snapshots, navigates, captures the new state, then animates old/new pseudo-elements.
- [Chrome for Developers: Cross-document view transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document?authuser=9) confirms that there is no `startViewTransition()` call for a normal cross-document navigation: a same-origin link navigation triggers it after both pages opt in. Chrome may skip a transition if navigation takes too long (the cited Chrome case is over four seconds).
- [MDN: `view-transition-name`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/view-transition-name) explains that named elements participate in separate snapshots and that names must be unique among rendered elements. Use stable names for a shared “paper stack” or title when moving between pages; remove temporary names after the transition if page state can persist in the back/forward cache.

Suggested page-level experiment:

```css
@view-transition { navigation: auto; }
.paper-stack { view-transition-name: paper-stack; }
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(*), ::view-transition-new(*) { animation: none; }
}
```

Use the transition as a page-turn or sheet handoff, not as the only way to understand navigation. Browser support and cross-document behavior are still newer than transforms/blending, so retain an ordinary link navigation fallback.

## Compact experiment sequence

1. Make three absolutely positioned light-paper sheets, each with one diagram fragment, a unique `z-index`, slight rotation, and a visible registration tab.
2. Toggle sheets with buttons and test `multiply` against a warm paper background; check text contrast with all combinations.
3. Add a volvelle-like circular index with keyboard-operable increment/decrement controls.
4. Add one flap interaction that reveals an underlying note while preserving normal DOM order.
5. If the site has multiple documents, opt both into same-origin view transitions and name only the shared stack; test back/forward navigation and reduced motion.
