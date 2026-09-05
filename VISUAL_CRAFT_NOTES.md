# Visual craft notes — interactive study material

Working reference for turning study-pack content into crafted, animated, scroll-driven
HTML instead of plain PDF/EPUB text. Started 2026-09-04. Add to this as we learn more —
this is a living notebook, not a spec.

## Working method (confirmed so far)

- Reuse the *engine* (grain texture, scroll-drawn line, reveal-on-scroll, reduced-motion
  handling) across pieces, but re-skin the *visual metaphor* per subject. Teoria do Delito
  (a crime passing through filters) got stamps/case-files/string. Usucapião (possession
  accruing over time) got a compass/topographic-lines/growing vine. Same technical
  toolkit, different world — that's what keeps it from feeling templated.
- Source content should come from the real study-pack markdown (`Coursework/*/luna_output/`),
  not be invented — the craft is presentation, not content generation.
- For a single dense creative pass where the whole composition needs to be reasoned about
  at once (palette, motif, motion, restraint), a stronger model (Opus) run as a background
  agent produces better results than fast iteration. Use it for the actual sample/deliverable,
  not for routine edits.
- Always give `prefers-reduced-motion` a real fallback, not just "less of the same" —
  static final-state, no parallax/scroll-timeline motion.

## Bugs hit / gotchas

- A fixed-position full-viewport `<svg>` with no explicit `width`/`height` does **not**
  stretch to fill the viewport just from `inset:0`. Per CSS spec, an absolutely/fixed
  positioned *replaced* element (which an `<svg>` with no dimensions is, using its
  intrinsic 300×150 default) with all four inset offsets set but `width`/`height: auto`
  resolves to its *intrinsic* size, not the containing block. Always set explicit
  `width:100%; height:100%` on a full-bleed fixed SVG overlay (e.g. a grain/noise texture).

## Techniques catalogued (not all used yet)

### Scroll & motion
- **CSS scroll-driven animations** (`animation-timeline: scroll()`, `view-timeline`,
  `animation-range`) — native, compositor-driven, no JS scroll listener. Universal
  browser support as of 2026. Use `animation-composition` when stacking e.g. rotate +
  translate on the same element so they don't overwrite each other. Feature-detect with
  `@supports (animation-timeline: scroll())` and provide a static/instant fallback.
  Used for: the string/vine that draws itself along the card spine as you scroll, and
  background-layer parallax at independent speeds via the `translate` property (not
  `transform`, so it composes cleanly with a layer's own static rotation).
- **Sticky-graphic + stepper text** (the Bloomberg/Pudding pattern) — a pinned
  illustration/diagram on one side, text steps scrolling past on the other, each step
  triggering a state change in the pinned graphic. Good candidate for a course concept
  that has one evolving diagram (e.g. a flowchart that highlights a new node per step)
  rather than discrete cards. Restraint matters here — Pudding/BMW examples that read
  well let the content carry weight and use animation sparingly, not on every element.
- **Branching-path narratives** — reader picks a path upfront (Pudding's IVF piece did
  "Parent vs Child" with distinct color accents per path). Could fit a legal doctrine
  with a real fork (e.g. "posse de boa-fé vs má-fé" outcomes diverging).

### Transitions & navigation
- **View Transitions API** (`document.startViewTransition()`) — native shared-element
  morph between two DOM states (or, cross-document, between two full page loads).
  Same-document transitions are Baseline since 2025. Being used now for the
  "pocket dimension" feature: click a card, it morphs into a dedicated full view for
  that concept. Give the clicked element a unique `view-transition-name`, feature-detect
  (`if (document.startViewTransition)`), and always keep a working instant-swap fallback.
  Respect reduced-motion by shortening/skipping the transition.
- **Cross-document View Transitions** (MPA, not SPA) — called out in 2026 coverage as
  "the single highest-leverage feature on the web platform" this year. Lets a real
  multi-page site (separate HTML documents/URLs, not one big single-file artifact) morph
  between pages natively, and combined with the Speculation Rules API (prerendering the
  likely next page) the navigation feels instant. **This matters for us specifically**:
  our single-file artifact approach doesn't scale to a real 400-page study pack — a real
  build would be multiple actual pages (one per chapter/concept) stitched together with
  cross-document view transitions, not one giant HTML file. Worth prototyping once we're
  past single-concept samples.
- **Popover API** — native, JS-light overlay primitive (`popover` attribute), stable
  across Chrome/Safari/Firefox since 2024. Good for footnotes, glossary terms, citation
  previews — no need to hand-roll a modal/tooltip system.
- **CSS Anchor Positioning** (`anchor()`, `position-anchor`) — tethers a positioned
  element to any other element declaratively, auto-flips on viewport overflow. Pairs
  with Popover API for zero-JS tooltips/definitions that stay attached to the term that
  triggered them (e.g. hovering a Latin term like *animus domini* popping a definition
  anchored right to it).

### Layout
- **Container queries** — size components to their container, not the viewport. Useful
  if we ever build a reusable "concept card" component that needs to look right whether
  it's in a wide two-column layout or a narrow pocket-dimension view.

## Texture / aesthetic direction

- **Risograph / "craftcore"** is the actual name for the "faux paper, crafted but sleek"
  direction. Riso printing (Riso Kagaku, Japan, 1986): limited saturated spot-ink palette,
  **misregistration** between color layers (1–3px offset, like a press slightly out of
  alignment), halftone/grain texture. CSS recipe: 2–3 saturated solid-color shapes with
  `mix-blend-mode: multiply`, offset by a couple px via custom properties, over an SVG
  `feTurbulence` noise mask. Apply sparingly at a few high-value spots (a seal, a divider
  rule, icon shadows) — not smeared across the whole page, or it stops reading as
  intentional.

## Samples built so far (as reference implementations)

- **Teoria do Delito** ("Dossiê do Delito") — case-file/dossier world. Wax seal in three
  riso-offset plates, washi tape, torn-paper card edges, red string drawn via scroll-
  timeline connecting six filter cards, background ghost-text watermarks + parallaxing
  "extra folders."
- **Usucapião** ("A Terra Muda de Dono") — land-survey world. Compass rose, topographic
  contour background, a vine drawn via scroll-timeline along the card spine, per-card
  mini plot-diagram that visually grows as requirements stack up. Currently getting the
  pocket-dimension click-through treatment (View Transitions API).

Both are published Claude Artifacts, not yet wired into the actual `rebuild_study_packs.py`
pipeline — they're proof-of-concept samples, not production output.

## Pocket dimensions

The user's framing, verbatim, because it's the clearest statement of the idea and worth
keeping exact: "put a pin on the idea of clicking each of those elements and it bringing
us to a whole like pocket dimension of that page meant for that thing specifically."

First build of this (on the usucapião piece) is in progress as of 2026-09-04, using
`document.startViewTransition()` so the clicked card morphs into a dedicated full view
rather than cutting to a modal. Each of the five requirements gets its own small themed
motif (flag-planting, empty courtroom, unbroken chain, accumulating year-rings, seal on a
ledger) plus real expanded doctrine content, not just the card text blown up bigger.

Open question once this lands: does a pocket dimension stay a single-document `<div>` swap
(what's being built now), or does it become an actual separate document/URL once we're
past sampling and into a real multi-page build? See the cross-document view transitions
note above — if pocket dimensions become real pages, that's the mechanism that makes
navigating into and back out of one feel seamless instead of a page-load jolt.

**Confirmed working pattern (built 2026-09-04 on the usucapião piece):** one shared
`view-transition-name` (not five separate ones) reassigned dynamically to whichever single
element is entering/leaving — the clicked card in the old state, the pocket panel in the
new one. Clear all other names first so exactly one element ever claims the shared name.
Hide the whole scroll page (`body.pocket-open` → `#shell{display:none}`) while a pocket is
open instead of building a real focus trap — nothing behind it is tabbable, so there's
nothing to trap. Panels are `role="dialog" aria-modal="true"`, focus moves to the panel on
open and back to the originating card on close, scroll position is saved/restored with
`behavior:'instant'` (the page's own `scroll-behavior:smooth` would otherwise animate the
restore). Fallback is identical behavior with no morph whenever
`document.startViewTransition` is missing or `prefers-reduced-motion: reduce` matches —
same DOM swap, just no animation. Catch the rejection on `viewTransition.ready`/`.finished`
or a skipped transition (backgrounded tab, reduced motion) logs an unhandled promise
rejection for no reason.

## Open questions — unresolved, don't paper over these

- **Does this scale past a sample?** A 400-page study pack can't reasonably be 400 pages
  of bespoke scroll-illustrated cards — that's not a rendering problem, it's an authoring-
  effort problem (an Opus pass per concept doesn't scale to hundreds of concepts across
  three courses). Likely resolution: this is a *highlight-reel* treatment for the concepts
  that are genuinely hard to hold as a mental model (the stuff the pedagogical-architecture
  memory is about), not a replacement for the full linear text. The PDF/EPUB stays the
  complete reference; the interactive piece is a small number of spotlight concepts per
  course, treated with real craft. Needs an explicit decision, not a default.
- **Relationship to the existing PDF/EPUB deliverables.** Supplement, not replacement —
  the interactive version needs JS/a modern browser and isn't something you read on an
  e-reader during a commute. Worth being explicit about this so nobody starts treating the
  scroll site as *the* study pack and lets the PDF go stale.
- **Where does it actually live / how is it read?** Right now everything is a Claude
  Artifact (claude.ai-hosted). That's fine for sampling but not a real answer for "the
  place you study from." Static export + something like GitHub Pages, or bundled as a
  local HTML file per course? Undecided.
- **Accessibility of a visually dense, motion-heavy format.** The plain PDF/EPUB is the
  accessible fallback almost by default (screen readers, text scaling, no motion). The
  interactive version needs its own pass on this, not an afterthought — Popover API and
  native semantics help, but a genuinely dense scrollytelling page is a different a11y
  surface than a linear document and deserves real attention before this becomes anything
  more than a novelty.

## Tangents, spin-offs, weird ideas — unfiltered, not yet vetted

- **A "desk" hub page.** Instead of jumping straight into one course's world, a landing
  page styled as looking down at a physical desk — each course is a folder/notebook/object
  on it, its own material and color already hinting at its visual world (the criminal-law
  dossier looks different from the property-law field notebook from across the desk) before
  you even open it. Ties the courses together as one object without forcing them into a
  shared visual language.
- **Generative/live grain instead of static SVG turbulence.** CSS Houdini paint worklets
  could render the paper noise procedurally so it very subtly shifts instead of being one
  frozen `feTurbulence` seed — probably imperceptible and possibly not worth the complexity,
  but it's the "proper" way to do it if we ever care.
- **Anchor-positioned glossary popovers.** Hover/tap a Latin term (*animus domini*, say)
  and a definition pops up tethered to that exact word via CSS anchor positioning + the
  Popover API — auto-flips if it would overflow the viewport, no JS needed. Worth
  prototyping on a real doctrinal term.
- **Choose-your-path branching**, borrowed from the Pudding's IVF piece pattern — a
  doctrine with a genuine fork (e.g. posse de boa-fé vs. má-fé, and how the consequences
  diverge) could let the reader pick a path and get a distinctly colored/accented track
  through the material instead of both outcomes flattened into one linear scroll.
- **Reading progress / resume-where-you-left-off**, via localStorage — scroll position or
  last-opened pocket dimension remembered per device. Small thing, but studying is
  session-based and nobody wants to re-scroll past six cards to get back to card five.
- **Print/export unification via something like Paged.js.** Right now the interactive
  build and `rebuild_study_packs.py`'s PDF output are two unrelated pipelines starting
  from the same markdown. Paged.js (or similar) can turn HTML/CSS into a proper paginated
  print PDF — if that ever converges, one source markdown could drive both the scroll
  experience *and* the printed PDF with actually shared styling, instead of two hand-tuned
  renderers drifting apart over time. Speculative, not scoped.
- **The top-left grain-texture bug was, in a dumb way, kind of fitting** — a ghost artifact
  bleeding out of a fixed corner on a page about legal filters and provenance boundaries.
  Not a real idea, just noting it because it was funny.
- **Cost/effort tiering across the three courses.** Not every course needs the same visual
  investment — if this direction continues, decide up front which course gets the "flagship"
  treatment (most bespoke motifs, most motion) versus a leaner shared template for the
  others, rather than discovering the imbalance after two are already built expensively.
- **Model-choice as a working pattern, not just a one-off.** Confirmed working split:
  Sonnet (this session) does orchestration, research, editing, and dispatching; Opus, run
  as a background agent, does the single dense creative pass that actually needs to sit
  and reason about a whole composition at once. Don't reach for Opus for iteration or
  routine fixes — reach for it for the pass that's actually the deliverable being judged.
  This mirrors the existing Claude/Luna split in [[feedback_pedagogical_architecture]]
  (Claude architects and edits, Luna does bulk volume) — here it's Sonnet architecting and
  Opus doing one very good single pass, which is a slightly different shape worth keeping
  distinct from the Luna pattern rather than conflating the two.
- **Explicitly NOT the same project as SEEU/PEC drafting or the arbitration work.** Those
  are separate active workstreams with their own rules (see the SEEU and arbitration
  memories). This craft/technique notebook is scoped to study-pack presentation only —
  don't let the two contexts bleed into each other just because both involve "legal
  documents and Claude."

## R&D log

**2026-09-04 — anchor-positioned glossary, built directly (no Opus dispatch, kept cheap
on purpose since the model-budget for this window was tight).** Contract-law running
prose (pacta sunt servanda, boa-fé objetiva, função social do contrato) with inline terms
that pop a tethered definition via native CSS Anchor Positioning (`anchor-name`,
`position-anchor`, `position-area`, `position-try-fallbacks`) + the Popover API
(`popover`, `popovertarget`) — genuinely zero JS for positioning. Sample:
`anchor-glossary-sample.html`, published at
https://claude.ai/code/artifact/f40f8d04-dd0a-4041-87c4-554e32309c76

**Verdict: worked, and verified for real, not just assumed.** Actually tested rather than
taken on faith — the Browser pane can't load our own claude.ai artifact URLs (needs
sign-in there), and a bare `file://` open of a scratchpad file only renders a static
snapshot with no JS, so verifying required serving the file over a throwaway local
`python3 -m http.server` and driving it from a second tab. Worth remembering as the
verification recipe next time an artifact needs real interaction testing rather than a
screenshot: **serve locally, don't trust `file://`, and don't assume the claude.ai
artifact URL is reachable from the Browser pane.**

Confirmed via `getComputedStyle`/`getBoundingClientRect`, not just visual inspection:
clicking a term opens its popover (`:popover-open` true), and the popover's rect sits
exactly `margin-top` below the button's rect with matching x — the tether is real, not
coincidental. `CSS.supports('position-area', ...)` and `CSS.supports('anchor-name', ...)`
both true in this environment (Chromium-based).

**One real bug this caught:** the interactive terms are `<button>` elements, and I'd reset
`background`/`padding`/`font` but not `border` — so every term rendered with the default
UA-stylesheet 2px outset black button border, invisible in a quick visual skim but
confirmed present via `getComputedStyle().borderTopWidth` before the fix. Reset `border`
explicitly whenever de-styling a native `<button>` used as a text-inline trigger; the
individual properties people usually remember (background, padding) don't imply the
others.

**Not yet tested:** the `position-try-fallbacks: flip-block, flip-inline` behavior when a
term sits close enough to the viewport edge to actually need the flip — the one edge-case
term tried in this pass had enough room and never triggered it. Also not tested: Firefox/
Safari behavior — `position-area`/anchor positioning lands there later than Chromium, and
the `@supports not (position-area: ...)` fallback (centers the popover instead of
tethering it) was written but only verified to have correct CSS, not exercised in an
actual non-supporting engine.

**Worth pursuing further:** yes — this is a genuinely different content shape (continuous
readable prose with embedded interactivity) than the card-based pieces, and it's cheap:
no scroll-timeline, no View Transitions, just two platform primitives that turned out to
compose cleanly. Good candidate for real course material once the flip-fallback and
cross-browser behavior get an actual test, not just a written fallback.

### 2026-09-05 — cross-checked against a parallel Codex attempt at the same brief

Owner ran the same "continue this" brief through Codex in parallel (`/Users/benecles/
Documents/Codex/2026-09-04/oka/`), separately from this notebook's own agents. Worth a
genuinely fair look rather than dismissing it, because two things in it are real and
worth keeping even though the overall approach isn't:

- **Codex built a full Next.js + shadcn/ui + Cloudflare Workers app** (~20 dependencies,
  50+ generic shadcn components with 4 actually used) instead of a single portable HTML
  file. That's a scope mismatch against the actual brief, not a style choice — don't
  repeat it. Its palette (`#f5f1e7` warm paper + `#ad4124` rust/terracotta) also landed
  almost exactly on the AI-slop cliché this whole design direction exists to avoid — a
  reminder that "risograph/craftcore" and "cream-and-terracotta AI default" are one bad
  color pick apart from each other; the misregistration/grain technique doesn't save a
  palette that's generic to begin with.
- **Correction to an earlier draft of this entry:** it initially credited Codex's more
  careful doctrinal writing (a "common misreadings, corrected" section, sharper fact-vs-
  doctrine hedging) as something worth copying. On reflection that's not actually a
  meaningful point of comparison here — **the legal content in every one of these
  samples is disposable placeholder**, a stand-in for the real study-pack markdown that
  already exists and is already correct (see the "working method" note at the top: source
  content should come from `Coursework/*/luna_output/`, not be authored fresh). None of
  these prototypes are testing content quality; they're testing presentation. So Codex
  spending real effort on doctrinal rigor for a throwaway vehicle topic isn't a win, it's
  a second instance of the same problem as the framework/architecture point above: solving
  a problem nobody was testing instead of the one actually in front of it. Don't chase
  "more careful legal writing" as a lesson from this comparison — that axis doesn't matter
  for R&D on the presentation layer.
- **A genuinely new idea neither of our own passes had**: it registered a tool via
  `document.modelContext` (`configure_time_diagram`, schema-validated, explicitly
  `readOnlyHint:false` but scoped to only ever touch the visible diagram state) so an AI
  assistant reading the page can *drive* an illustrative diagram directly instead of only
  describing it. Untested by us, and needs its own scrutiny (what is `modelContext`,
  whose API is it, does it only exist in some host?) before reuse, but the concept — a
  study page exposing a narrow, harmless tool surface for an assistant helping a reader —
  is worth a real prototype at some point.
- **Its research memo caught three concrete technical corrections ours didn't have**,
  confirmed against MDN and worth treating as true regardless of source:
  1. `scroll-timeline` does not activate on a source element with no actual overflow (or
     one that's clipped/hidden) — a `view-timeline`/scroll-timeline animation can silently
     never run if the driving element never overflows its container.
  2. The `animation` shorthand resets `animation-timeline` if the shorthand is declared
     *after* it — always set `animation-timeline` (and `animation-range`) after any
     `animation:` shorthand on the same rule, not before.
  3. Popover UA-stylesheet defaults (`inset`, `margin`, sometimes `position`) can override
     an intended anchor placement if left unreset. **Checked why our own
     `anchor-glossary-sample.html` avoided this despite never resetting `inset` — it's not
     luck, it's ordinary cascade**: `position-area` itself resolves to the inset
     longhands, and any author-stylesheet declaration beats a user-agent stylesheet
     declaration of the same properties regardless of selector specificity (origin
     precedence outranks specificity in CSS's cascade order). So declaring `position-area`
     on `.gloss` automatically overrode the UA default `inset:0` with no separate reset
     needed. Worth knowing this actually, not assuming it: **`margin` still needs an
     explicit reset** (as this sample already does) because nothing about `position-area`
     touches `margin`, and a popover's UA-default `margin: auto` can still shift it off
     the anchored position that `inset`/`position-area` computed.

**Verdict:** don't adopt the framework/architecture, do adopt the three MDN-confirmed CSS
corrections above (the content-rigor point was retracted, see the correction right above
this line — content quality isn't the axis being tested here). The `modelContext`
tool-exposure idea is now a *verified*, not just plausible, open item — see below.

### 2026-09-05 — WebMCP (`document.modelContext`) verified real, not available here to test

Followed up on the open item above. `document.modelContext.registerTool()` is a real,
current proposal — **WebMCP**, from the W3C Web Machine Learning Community Group,
authored by Microsoft and Google engineers, first announced Feb 2026, currently in a
Chrome origin trial and (per press coverage, not independently confirmed by us)
default-on for some Shopify/Cloudflare-fronted sites as of August 2026. The naming has
already shifted once — it started as `window.agent`, shipped briefly as
`navigator.modelContext`, and Chrome's plan is to deprecate that in favor of
`document.modelContext`. So: not invented, genuinely cutting-edge, but also genuinely
unstable API surface — expect the name/shape to keep moving.

The idea itself: a page registers a small, schema-validated, scope-limited tool (e.g.
"set these illustrative years on this diagram") that an AI agent visiting the page can
discover and call directly, instead of only being able to read/describe the page. For a
study page, that could mean an assistant helping someone read *actually drives the page's
own illustrative controls* rather than just talking about them.

**Checked in our own testing environment and it is not available**: this session's
Browser-pane Chromium build (Chrome 148, no origin-trial token) has neither
`document.modelContext` nor `navigator.modelContext` — confirmed via direct
`'modelContext' in document`/`in navigator` checks, not assumed. This is exactly why
defensive feature-detection (`if (!context?.registerTool) return`, wrapped in try/catch)
is the only correct way to touch this API right now, which — credit due — is how the
Codex piece actually wrote it.

**Verdict: real, interesting, not yet testable by us, worth a real prototype once it's
reachable** (either a Chrome build with the origin trial enabled, or once it ships more
broadly). Don't build anything that depends on it working today. Worth revisiting this
entry periodically since the API name/shape is explicitly still moving.

### 2026-09-05 — audited all five samples against the animation-shorthand ordering bug

The `web-mechanics.md` memo's correction #2 above (the `animation` shorthand silently
resets `animation-timeline` if the shorthand comes *after* it) is the kind of bug that
produces no error and no visual symptom except "the scroll effect just never runs" — easy
to ship unnoticed. Grepped all five samples for every `animation:`/`animation-timeline`
pair. **Clean across the board**: `dossie-craft-sample.html`, `usucapiao-sample.html`,
and `bifurcacao-constitucional.html` (the three that use scroll-timeline/view-timeline at
all) all declare `animation-timeline` as its own property strictly after the `animation:`
shorthand in every rule that uses both. Nothing to fix, but worth having actually checked
rather than assumed — this is exactly the class of bug the CSS grain-sizing one from
earlier belonged to.

### 2026-09-04 — "Bifurcação Constitucional": sticky stepper + trilha bifurcada + glossário ancorado, sem JS

**Artefato:** https://claude.ai/code/artifact/d3848c6e-66d3-4ce8-af6a-5baae8e7b3d9
**Arquivo:** `bifurcacao-constitucional.html` (scratchpad da sessão f4d3bdb8).
**Assunto:** controle de constitucionalidade (difuso × concentrado) — escolhido de fora da grade
do dono, só como veículo. É a doutrina que mais claramente *é* uma bifurcação: mesma pergunta,
duas rotas, consequências que divergem de verdade (inter partes/ex tunc vs. erga omnes/vinculante).

**O que tentei, e por quê.** Três das ideias da seção de tangentes ao mesmo tempo, porque as três
são baratas de descrever e caras de descobrir só no papel:

1. **Sticky-graphic + stepper (padrão Pudding/Bloomberg)**, mas 100% em CSS scroll-driven — sem
   IntersectionObserver, sem scrollama, sem listener nenhum.
2. **Bifurcação de trilha** — o leitor escolhe a via e a página inteira troca de conteúdo e de cor
   de acento.
3. **Glossário em popover ancorado** — CSS anchor positioning + Popover API para os termos
   (*erga omnes*, *ex tunc*, reserva de plenário, pertinência temática…).

Meta autoimposta que virou o experimento de verdade: **zero `<script>` no arquivo**. Cumprida.
Os dois samples anteriores têm JS (o de usucapião tem bastante, por causa das pocket dimensions).
Esse não tem uma linha.

**Mundo visual.** Desenho de corte estrutural / prancheta de engenharia — a Constituição como
fundação hachurada, a lei como viga apoiada nela, os vícios como fissuras, o controle preventivo
como uma treliça de inspeção acima, e a bifurcação como duas rotas de carga descendo. Concreto
frio (`#dcdad2`), grafite, e as duas vias como as únicas cores saturadas da página: azulejo
`#2f6088` para o difuso (disperso, pontilhado, muitos nós) e óxido de ferro `#8e3a26` para o
concentrado (uma linha só, grossa, contínua). Tipos: **Archivo variável no eixo `wdth`**
(display expandido 112, rótulos condensados 84 — mesma família fazendo dois trabalhos opostos),
**Spectral** no corpo, **IBM Plex Mono** nas cotas e rótulos do desenho. Nenhuma das três aparece
nos samples anteriores, de propósito.

**O que funcionou melhor do que eu esperava**

- **`view-timeline-name` na própria `<section>` + `animation-range: contain X% contain Y%` por
  peça do desenho.** Esse é o achado técnico da rodada. Declarando a timeline na seção (ancestral
  comum do gráfico fixo e da coluna de texto) não precisei de `timeline-scope` — que é a parte
  menos suportada da especificação e que eu ia usar por instinto. A faixa `contain` de um elemento
  mais alto que a viewport corresponde *exatamente* ao período em que o sticky fica preso, então
  0%→100% da timeline = começo→fim do pin. Cada estágio do desenho vira uma linha de CSS:
  `.s4{ animation-range: contain 49% contain 55%; }`. Seis estágios, seis linhas.
- **Passo ativo aceso sem observer.** Cada bloco de texto usa a *própria* `view()` com
  `animation-range: cover 18% cover 82%` e keyframes `0%{opacity:.28} 36%,64%{opacity:1}
  100%{opacity:.28}`. É literalmente o efeito "step em foco" do scrollytelling clássico, em cinco
  linhas de CSS e sem estado em JS. Se algum dia isso virar pipeline, esse trecho é reutilizável
  como está.
- **Bifurcação com `:has()`.** Dois `<input type="radio">` visualmente ocultos dentro de um
  `<fieldset>`, e `body:has(#via-d:checked){ --via: var(--difuso); }`. A troca de acento propaga
  por token para trilho, marcadores, bordas, links e `:focus-visible` de uma vez. Acessível de
  graça (é um grupo de rádio de verdade, navegável por teclado) e a trilha não escolhida sai da
  árvore de acessibilidade sozinha via `display:none`. Nada disso precisou de JS.
- **Popover ancorado.** `position-area: block-start span-inline-end` +
  `position-try-fallbacks: flip-block, flip-inline` — a definição nasce colada ao termo e vira
  sozinha quando não cabe. Confirmado funcionando: clicando "maioria absoluta" no meio de um
  parágrafo, o balão apareceu exatamente acima da palavra.

**O que foi mais chato do que parecia**

- **`overflow-x: hidden` no `body` mata `position: sticky`.** Tirei antes de bater no problema
  porque lembrei do risco, mas fica anotado: os dois samples anteriores têm essa linha e nenhum
  deles usa sticky. Quem copiar o CSS de lá para uma peça com gráfico fixo vai perder meia hora.
- **Ancoragem implícita não basta.** Em tese um elemento com `popovertarget` já é âncora implícita
  do seu popover e daria para não nomear nada. Não confiei: pus `anchor-name` inline em cada botão
  e `position-anchor` inline em cada popover. Nove pares de `style=` feios, mas determinístico.
- **Regras globais de traço vazam para os SVGs decorativos.** `.route-d/.route-c` ganharam
  `stroke-dashoffset:220` para se desenharem no scroll, e isso apagou as mesmas classes usadas nos
  ícones da capa e dos botões de escolha. Correção certa foi escopar (`.drawing .route-d`), não
  remendar com `style=` inline nos ícones — que foi minha primeira tentativa.
- **Rótulo dentro de desenho técnico é um problema de composição, não de CSS.** O rótulo do
  controle preventivo caía em cima das diagonais da treliça; só resolveu movendo a barra horizontal
  do desenho e reposicionando o texto na faixa de baixo. Desenho SVG à mão custa tempo justamente
  aqui, não nos `path`.
- **Em viewport curta o gráfico fixo mobile fica pequeno demais.** `clamp(210px, 44svh, 340px)`
  com um viewBox 400×500 dá uns 270px de largura. É o teto do padrão sticky no celular; não tem
  truque, só aceitar ou desenhar um segundo viewBox mais largo para telas baixas. Não desenhei.

**Não tentei:** grain via Houdini paint worklet. `CSS.paintWorklet.addModule()` precisa de uma URL
de módulo, e a única forma dentro de um arquivo único seria `blob:`, que a CSP do Artifact
provavelmente barra em `script-src`. Continua sendo pergunta aberta — mas agora com uma hipótese
concreta do porquê pode não dar. Ficou o `feTurbulence` de sempre.

**Veredito.** Vale continuar, com prioridades bem diferentes entre as três coisas:

- **O stepper CSS-only é o item que vale levar adiante.** É a técnica que melhor se encaixa no
  problema real do caderno (conceito com *um* diagrama que evolui, em vez de N cards discretos) e é
  a mais barata de repetir: o esqueleto CSS é genérico, só o SVG muda. Candidato natural a virar o
  bloco reutilizável do pipeline.
- **A bifurcação é boa, mas é cara em conteúdo, não em código.** O CSS são seis linhas; o custo é
  ter duas trilhas doutrinárias reais e paralelas escritas. Só compensa em doutrina que
  *genuinamente* bifurca — controle de constitucionalidade e posse de boa-fé/má-fé compensam;
  a maioria dos tópicos não, e forçar uma escolha onde não há fork vira interação decorativa.
- **O glossário ancorado é o melhor custo-benefício da rodada** e não deveria ser tratado como
  técnica de peça especial: é candidato a entrar em *todas* as peças, inclusive nas duas já
  publicadas. Escreve-se um `<button popovertarget>` e um `<div popover>`, e pronto.

Sobre a pergunta de escala que está lá em cima: essa peça não a resolve, mas mexe no cálculo. Tem
seis passos ilustrados, duas trilhas e nove verbetes, e o único item caro de produzir foi o SVG do
corte. Se o diagrama fosse gerado a partir de um esquema simples em vez de desenhado à mão, esse
formato específico — um diagrama fixo que evolui, não N cards bespoke — é bem mais reprodutível do
que os dois samples anteriores. Não é a resposta, mas é a primeira evidência de que existe um
subconjunto barato dessa estética.

---

# Codex R&D — separate continuation, started 2026-09-04

**Attribution boundary.** Everything above this divider is the earlier Claude-led notebook,
preserved unchanged. Entries below are Codex's own investigations, prototypes, judgments,
and open questions. Research assistance from Luna is credited where incorporated. Earlier
claims are historical observations, not automatically re-verified findings of this phase.

## Round 1 — brief, questions, and work in progress

The owner authorized open-ended research and experimentation, with the creative design and
synthesis kept with the primary Codex model and less expensive agents used for bounded
research. The owner also explicitly requested continuing this living notebook, including
intriguing things, tangents, questions, bugs, and possible ideas, with clear authorship.

**Starting hypothesis:** a complete study reader may combine a quiet, strongly designed
reading surface with selective interactive depth. Hundreds of individually animated scenes
are not the only way to preserve the aesthetic through hundreds of pages. This is a
hypothesis, not evidence of scalability or improved learning.

Questions for this round:
- Can a reader move between a continuous argument, a spatial overview, and a deeper concept
  view without losing their place?
- When does a material metaphor explain the subject, and when is it merely decoration?
- Does a concept's illustration become more useful when the reader controls a variable?
- What should remain visually stable on the fifth visit, when finding matters more than
  experiencing the entrance animation?

**Initial handoff observation:** the five exported HTML files show mojibake when served by a
plain local HTTP server without an explicit UTF-8 response charset. At least the dossier
source starts with `<title>` and lacks a charset declaration. Source text is UTF-8. This
was observed in the Codex browser; it is a portability issue, not a judgment about their
original Claude Artifact rendering. The old samples were not edited.

Work in progress: two Luna research passes on reading precedents and browser mechanics,
plus a narrow official-source content check. Root owns the prototype and final synthesis.
Experiment workspace: `/Users/benecles/Documents/Codex/2026-09-04/oka/work/notes-lab`.

## Round 1 — findings, experiments, and things worth not forgetting

**Authorship:** primary Codex model designed and implemented the reader and wrote this
synthesis. Luna supplied three bounded research memos: reading-interface references,
primary browser documentation, and an official-source check of the statutory nucleus.
The prototype reuses the *subject* of the earlier usucapião sample, making a comparison
possible, but its layout, code, diagrams, and authored interaction structure are new.

### What the internet contributed

- **Liza Daly's Harmonia / interactive marginalia** was the most useful unexpected find.
  A clicked phrase changes its underline, and its annotation remains alongside the text.
  The interesting part is the memory left in the reading surface. Daly also documents
  collision bugs from absolute positioning and the irritation of replaying animations.
  We adapted the persistence idea using a normal-flow margin, avoiding a new connector-
  routing/collision problem in this first round. Source:
  https://lizadaly.com/essays/interactive-marginalia/
- **Bret Victor's Explorable Explanations** suggests a stricter criterion for an
  interactive diagram: it should let a reader question an assumption inside the author's
  explanation. Applied here: change elapsed years and the reduced-period hypothesis,
  while explanatory text states exactly what the model does and does not establish.
  Source: https://worrydream.com/ExplorableExplanations/
- **Distill's article conventions and research synthesis** are useful for combining
  ordinary prose with details on demand. They also discuss substantial authoring and
  maintenance costs. Their research does not validate this prototype's learning value.
  Sources: https://distill.pub/guide/ and
  https://distill.pub/2020/communicating-with-interactive-articles/
- **Andy Matuschak's working notes** made the overview/detail question concrete: linked
  concepts can be explored while retaining context. We did not copy the horizontal note
  stack. The current reader keeps one deeper sheet and explicit return behavior.
  Source: https://notes.andymatuschak.org/
- **Bartosz Ciechanowski's Moon** is an aspirational reference for multiple views of the
  same underlying model. A promising future law version might show an argument from two
  parties' perspectives, provided the differences are authored and grounded rather than
  generated by an unaccountable rule widget. Source: https://ciechanow.ski/moon/
- **The Pudding's storytelling writeup** is a reminder that readers skip and reverse.
  A scroll position is an unreliable proxy for having understood the preceding step.
  Source: https://pudding.cool/process/how-to-make-dope-shit-part-3/

### Experiment A — a chapter with three different depths

Built **Caderno de campo: Posse, tempo e domínio**. One continuous chapter, three deeper
concept sheets, one short glossary definition, one persistent margin note, chapter anchors,
a device-local reading marker, and a quieter reading view. The diagrams are explanatory
geometry. No representational raster artwork or inherited sample code was used.

The three depths deliberately do different jobs:
1. A brief glossary answer can temporarily sit over the page.
2. A margin note remains beside its passage and can survive a reload.
3. A concept sheet contains enough additional explanation and a different diagram to
   justify leaving the main reading surface temporarily.

**Observation:** the browser exercised all three types. The concept sheet's Escape close
returned focus to its exact originating button; the recorded main-page scroll offset
was unchanged (1423.18 px before/after in that check). Back left the sheet, Forward
reopened it. Direct query URLs carry the concept identifier. Reload restored the open
margin and the saved chapter marker after client hydration.

**Judgment, not measured outcome:** different depths seem more promising than making every
click open the same generic card. A definition, an aside, and a digression have different
weights. This is still one reader and one short chapter, not a comprehension study.

### Experiment B — a diagram that answers a bounded question

The opening plate uses concentric ellipses, one per year. The reader changes elapsed years
and a reduced-period switch. The marked reference boundary moves between 15 and 10 years.
At 10 years, the reduced-period hypothesis reaches the reference period; the general rule
does not. That is the entire model. It never declares someone the owner.

**Verified:** setting 10/reduced returned a 10-year period reached; the keyboard Home key
moved the slider to zero and the displayed remaining period updated. The structured
browser tool uses the same React state and rejects a year outside 0–15 before mutation.

**Ambivalence worth retaining:** the contours give the subject a material identity, but a
conventional bar is easier to read precisely. The successor-possession sheet consequently
uses a 6 + 9 proportional bar. Do not insist that the most atmospheric drawing is also
the best analytical representation. A future experiment could pair a compact bar and
contour drawing and ask which question each helps answer.

**Content constrained the design, usefully.** The earlier exports included broad statements
about tenants never acquiring by usucapião, any judicial action interrupting time, and a
judgment creating the title. The official-source check led us to avoid those absolutes.
The new timeline intentionally cannot simulate contested legal events with simplistic
switches. Source: Código Civil, arts. 1.196–1.198, 1.208, 1.238, 1.241, 1.243–1.244:
https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html

### Experiment C — revisiting instead of replaying

Chapter anchors and a remembered chapter offer re-entry without scrolling through the
opening. The margin leaves a highlight on the triggering words and remembers its state.
The **Só leitura** control removes the opening diagram and reduces visual density while
keeping the chapter and its concept links. Preferences live in this browser only.

**Observed limitation:** the current pocket is a modal presentation over the same document,
with a meaningful URL. It is not a tested cross-document transition or a fully independent
chapter page. A direct link can restore the concept, but cannot reconstruct a different
visitor's previous reading position. Closed concept text is not in the DOM, so browser
Find does not search it. This matters a lot more at course scale.

### Bugs, implementation notes, and qualifications

- The source now has normal UTF-8 HTML metadata through the framework; accents rendered
  correctly in the new prototype. The original exports remain unchanged.
- A `pushState` alone does not implement Back behavior: the pocket also listens for
  `popstate`. Direct entry must be distinguished from a sheet opened inside the reader,
  or the close button can accidentally take the visitor out of the site.
- Focus restoration is explicit. The primary page stays mounted under the accessible
  dialog primitive, preserving its scroll and reading state.
- The app initially renders server text, then hydrates stored preferences. A snapshot
  immediately after reload can show defaults before the stored margin/marker reappear.
  Verification waited for the actual remembered note rather than declaring it broken.
- Reading-marker writes begin after user navigation/scrolling. Merely loading the top of
  a page should not immediately overwrite the useful marker from the previous session.
- Some early labels were too small. They were raised, and the acquisition/declaration/
  registration diagram switches to a vertical sequence on narrow screens.
- Tested in the available Chromium-based browser at wide and narrow viewports, with real
  interaction. This is not evidence of Safari/Firefox equivalence or full accessibility.
- Reduced-motion CSS and the no-View-Transitions branch are implemented; an actual
  alternate-engine/reduced-motion device run remains open. Print CSS is present but
  print pagination and tagged-PDF accessibility have not been verified.
- The supplied starter has existing whole-project lint issues in its component catalog.
  Those unrelated files were preserved. App-source lint and TypeScript are checked
  separately; the production build succeeds. Do not describe whole-template lint as green.
- Unlike Claude's no-script experiment, this round uses JavaScript and supported UI
  primitives where they simplify reliable behavior. Zero JS is an interesting experimental
  constraint, not evidence of a better reader.

### Corrections to assumptions in the earlier notebook — not edits to its history

The earlier wording about universal scroll-timeline support should not be carried forward
as a guarantee. Treat it as progressive enhancement and inspect actual target browsers.
Baseline is about a defined browser set, not every older release, webview, or assistive
technology combination. PDF is not automatically an accessible fallback either: tag order,
reading order and alternative text need verification.

Primary documentation collected by Luna:
- https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/scroll-timeline
- https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using
- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/hidden
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility
- https://www.w3.org/WAI/WCAG21/Techniques/pdf/PDF3

### Tangents and next experiments — deliberately unresolved

- **Search that opens depth.** `hidden="until-found"` plus `beforematch` is worth testing
  for collapsed authority/exception text. Can browser Find reveal the right conceptual
  layer, retain the match, and provide a natural way back? Current modal content cannot.
- **A change of lens without a change of address.** Doctrine, example, counterexample,
  source passage. Could these be adjacent representations of the same concept, with a
  stable title and location, rather than four separate destinations?
- **Annotation provenance as a visible layer.** Statute, teacher's emphasis, author's
  paraphrase, student question: distinguish them by meaning and label. Color alone would
  be insufficient. A crafted page must not make a paraphrase look like authoritative text.
- **Bookmarks with a reason.** A marker saying “return to this exception” might be more
  useful than a scroll percentage. Need to learn whether writing it costs too much effort.
- **The second legal world.** This prototype retains the land-study world. Test a subject
  whose shape is genuinely different before declaring that the system generalizes.
- **A real long chapter.** Use 20–30 pages of supplied course content, preserve all nuance,
  and test sustained reading, direct retrieval, browser search, and phone use. Repeated
  filler paragraphs would test rendering, not authoring quality or reading usefulness.
- **Authorship economics.** Separate stable layout/navigation code from authored diagram
  models and high-value editorial judgments. Measure effort on a second chapter before
  promising cheap scaling.
- **The physical desk hub** still intrigues me, but navigation should earn its metaphors:
  a beautiful folder that adds friction on every visit may be the wrong front door.

**Current synthesis:** we have a working example of quiet prose and selective depth sharing
one visual identity. We do not yet know whether it improves retention, whether a whole
course feels coherent, or what it costs to author at scale. Those are the next meaningful
questions, not whether another entrance animation is possible.

---

# Claude R&D — retomada 2026-09-05 (homepage, glossário, paleta, e dois bugs reais)

**Fronteira de autoria.** Volta ao caderno original liderado por Claude. As entradas
do Codex acima ficam preservadas. Esta rodada foi um passe de design/polimento pedido
pelo dono, com quatro frentes declaradas e duas que apareceram no meio do caminho.

## O bug do diagrama fixo: a causa real, e por que a teoria "óbvia" estava errada

O dono relatou que o diagrama estrutural de `bifurcacao-constitucional.html` **"já
aparece pronto"** no Safari, em vez de se montar conforme o scroll. Antes de mexer,
vale registrar **tudo o que foi descartado com medição, não com palpite** — porque
cada um desses era um candidato plausível e três deles são a resposta errada:

1. **"Safari não suporta `animation-timeline: view()`."** Falso, e o dono já tinha
   confirmado. Medido de novo neste Mac: Safari 26.6 responde `true` para
   `CSS.supports` em `animation-timeline: view()`, `animation-timeline: scroll()`,
   `view-timeline-name`, `animation-range: contain …` e `animation-range: cover …`.
2. **"A `@media (prefers-reduced-motion: no-preference)` está barrando o bloco."**
   Falso: `matchMedia('(prefers-reduced-motion: reduce)').matches` é `false` aqui.
3. **"A view-timeline está inativa."** Falso *na máquina real* — mas esta foi a
   armadilha da rodada, ver a seção sobre o painel do navegador abaixo.
4. **"Os `animation-range` completam nos primeiros %."** Falso: instrumentando a
   página real no Safari, as seis `.stage` vão de `opacity 0.00` a `1.00`
   escalonadas ao longo de todo o pin (`s1` em ~20%, `s4` em ~50%, `s6` em ~86%).
   **A montagem em seis estágios sempre funcionou.**

**A causa real: o "desenho" das duas rotas nunca foi um desenho.** O que o leitor
percebe como "já está pronto" não é a montagem dos estágios — é a bifurcação, que
aparece inteira de uma vez. O CSS fazia:

```css
.drawing .route-d, .drawing .route-c{ stroke-dashoffset:220; animation:draw …; }
@keyframes draw{ to{ stroke-dashoffset:0; } }
```

e isso é **visualmente inerte nas duas rotas, por dois motivos diferentes**:

- `.route-c` (concentrado, traço sólido) **não tem `stroke-dasharray` nenhum**. Sem
  padrão de tracejado, `stroke-dashoffset` não tem o que deslocar: é um no-op
  absoluto. A rota sólida esteve 100% desenhada desde o primeiro quadro em que o
  grupo `s6` ficou visível.
- `.route-d` (difuso) tem `stroke-dasharray: 5 7` — mas isso é o **pontilhado
  decorativo** da via difusa ("disperso, pontilhado"), um padrão que se repete a
  cada 12 unidades. Animar o offset de 220 a 0 num padrão repetido apenas
  **desliza os pontos ao longo do caminho**; nunca revela o caminho.

A técnica clássica de line-drawing exige que o dash seja *do tamanho do traço
inteiro* (`pathLength="1"` + `stroke-dasharray:1` + offset 1→0 — que é exatamente,
e corretamente, o que a videira do usucapião faz). Aqui a mesma propriedade estava
sendo pedida para fazer dois trabalhos incompatíveis ao mesmo tempo: **ser o
pontilhado e ser a máscara de revelação**. Não dá.

Confirmado visualmente, não só numericamente: capturas em `contain 92%` mostravam
as duas curvas completas, com os nós já pousados na fundação, enquanto o
`strokeDashoffset` computado ainda marcava `90px`. O valor mudava; os pixels não.

**A correção.** Trocar a revelação por um **clip retangular que cresce em Y**
(`<clipPath>` com um `<rect class="reveal-wipe">`, `transform-box:fill-box;
transform-origin:top`, animado de `scaleY(0)` a `scaleY(1)` na mesma
`animation-range: contain 84% contain 97%`). Vantagens sobre voltar ao dashoffset:

- funciona igual para o traço sólido e para o pontilhado, **sem tirar o pontilhado**
  da rota difusa — que é semântico nessa peça, não decoração;
- as duas rotas descem da viga para a fundação, então uma varredura de cima para
  baixo *lê como a carga descendo*, que é o próprio assunto do desenho;
- o estado-base (`transform:none`) é "revelado", então o recuo de
  `prefers-reduced-motion` e de navegador sem suporte continua correto de graça.

Os dois rótulos (`difuso` / `concentrado`) ficaram **fora** do grupo clipado, senão
sumiriam até o final da varredura.

**Verificado nos dois motores, não deduzido.** Safari 26.6 nesta máquina, na página
real: `scaleY` progride `0 → 0.305 → 0.687 → 1.0` e a altura renderizada do rect de
clip vai de `0px` a `137px` ao longo da faixa. Chromium headless: idem, com
capturas mostrando as curvas cortadas no meio em 90% e completas em 100%.

**Lição transferível:** `stroke-dashoffset` só existe se `stroke-dasharray` existir,
e só *revela* se o dash cobrir o traço inteiro. Um `stroke-dasharray` decorativo e
uma animação de revelação são usos mutuamente exclusivos da mesma propriedade. Se a
peça precisa das duas coisas, a revelação tem que sair da propriedade de traço e ir
para um clip/máscara.

## Modo quirks em todas as quatro peças — o bug de portabilidade que ninguém viu

Achado no caminho, e provavelmente **a explicação do "no celular fica estranho"**.

As quatro páginas de experimento começavam direto em `<title>`: **sem `<!doctype
html>`, sem `<meta charset>`, sem `<meta name="viewport">`.** Isso é resíduo de
terem nascido como Artifacts do claude.ai — o host embrulha o conteúdo num
esqueleto `<!doctype html>…<head>` na hora de publicar. Ao exportar os arquivos
crus para um repositório servido pelo GitHub Pages, o embrulho não veio junto.

Consequências medidas (`document.compatMode === "BackCompat"`,
`document.characterSet === "windows-1252"`, `document.scrollingElement === BODY`):

1. **Sem `viewport`** o celular renderiza a 980px e reduz tudo — que é exatamente o
   sintoma "roda bem no Mac, no telefone parece errado". Este era o item mais caro.
2. **Sem `charset`**, qualquer servidor que não mande `charset=utf-8` no cabeçalho
   produz mojibake (o Codex já tinha anotado isto na Round 1 dele; estava certo, e
   a causa é esta). O GitHub Pages manda, então a acentuação escapava na produção
   — mas quebrava em qualquer servidor local.
3. **Modo quirks** em si: aqui ele **não** quebrou as scroll-timelines (medido nos
   dois modos no Chromium: idênticos), mas é dívida técnica gratuita.

Corrigido nas quatro com um preâmbulo mínimo (doctype + `<html lang="pt-BR">` +
charset + viewport); `<head>` fica implícito, já que `<title>`/`<style>` vêm antes
de qualquer conteúdo de corpo. **Se outra peça nascer como Artifact e for exportada,
esse preâmbulo é obrigatório na exportação.**

## O painel de navegador mente sobre scroll-timelines quando está escondido

Custou muito tempo e vale ficar registrado em destaque, porque **produziu um
diagnóstico falso e quase produziu uma "correção" para um bug inexistente**.

No painel Browser desta sessão, `document.hidden === true`. Com o documento não
sendo renderizado, **toda `ViewTimeline` reporta `currentTime === null`** — ou seja,
inativa — e as animações ligadas a ela não aplicam nada. O que se vê então é o
**estilo-base** da regra, o que gera duas leituras enganosas opostas:

- em `.stage{opacity:0; animation:…}` → parece "o desenho nunca aparece";
- num elemento sem opacidade base → parece "já está tudo pronto".

Foi exatamente esse o falso positivo do relato paralelo sobre a videira do
usucapião (`strokeDashoffset` travado em `1px`, `.stages` com `width === 0`).
**A videira não tem bug**: medida com renderização real, ela vai de `1` a `0` e
completa por volta de 75% do scroll do documento. O `width: 0` era leitura de um
`<svg>` cujo `getBoundingClientRect` não é comparável ao do elemento HTML pai.

**Receita de verificação que funcionou** (sucessora da receita "sirva local, não
confie em `file://`" da entrada de 2026-09-04, que continua válida e agora ganha
uma camada):

1. `python3 -m http.server` para servir os arquivos;
2. **Chrome headless real via CDP** (`--headless=new --remote-debugging-port`),
   dirigido por um script Node de ~20 linhas usando o `WebSocket` global do Node —
   sem puppeteer, sem dependência nenhuma. `Emulation.setDeviceMetricsOverride`
   dá viewports de celular de verdade e `Page.captureScreenshot` dá as imagens.
   **Aqui `document.hidden` é `false` e as scroll-timelines funcionam.**
3. Para o Safari real, sem poder digitar dentro dele: abrir com `open -a Safari` uma
   **cópia instrumentada** da página que roda o diagnóstico sozinha e devolve o
   resultado com `fetch('/REPORT/'+encodeURIComponent(json))` — o caminho aparece no
   log do próprio `http.server`, que é só ler. Truque barato e sem permissões.

Regra prática: **nunca conclua "a scroll-timeline não está rodando" sem antes
checar `document.hidden`.**

## Homepage: mesa de luz, não mesa de trabalho

A `index.html` era um catálogo funcional (título + quatro linhas com bolinha
colorida). Virou peça desenhada. Pesquisa consultada: convenções de Page Previews
da Wikipédia, Tufte CSS / sidenotes do gwern, e — mais útil que qualquer referência
externa — **o próprio caderno**: a ideia da "mesa física" da seção de tangentes,
somada ao aviso do Codex de que *"navegação precisa merecer suas metáforas: uma
pasta bonita que adiciona atrito em toda visita pode ser a porta de entrada errada"*.
Esse aviso foi acatado: **não** virou uma escrivaninha skeuomórfica.

O que ficou: **ardósia escura e neutra, e cada experimento é uma "chapa" luminosa
pintada na paleta da própria peça.** O hub não escolhe um estilo — ele é a moldura,
e as quatro peças fornecem a cor. Isso resolve o pedido do dono ("não precisamos
escolher um estilo pro conjunto") de forma literal, e entrega o efeito que a
tangente da mesa queria: **dá pra distinguir o arquivo criminal do caderno de
agrimensor de longe, antes de abrir**. Cada chapa é um SVG desenhado à mão com os
motivos reais da peça (selo de cera em três chapas riso; rosa dos ventos + curvas de
nível + videira; prosa com termo aceso e ficha ancorada; corte estrutural com as
duas rotas divergindo), nos hexadecimais reais de cada arquivo.

Tipografia deliberadamente inédita no conjunto: **Bricolage Grotesque** (display),
**Literata** (corpo), **Martian Mono** (rótulos). Nenhuma das três aparece nas
quatro peças.

**Arquitetura que pode crescer, sem conteúdo falso.** O dono cogitou seções futuras
de "study packs" e de "aulas do semestre", e explicitamente pediu para **não**
construir isso agora. O único gesto feito foi dar aos experimentos uma **faixa de
seção numerada** (`01 — Experimentos`), de modo que um `02` posterior seja adição
óbvia em vez de reforma. Zero placeholders, zero "em breve".

## Glossário: o cartão perdeu o contorno e o termo ganhou memória

O dono gosta do mecanismo (anchor positioning + Popover, zero JS) e desconfiava do
tratamento visual — forma retangular, borda. Estava certo: era um retângulo de
cantos vivos com borda de 1px sobre um fundo *mais escuro* que a página, ou seja,
lia como caixa de diálogo de aplicativo, não como aparato editorial.

O que a pesquisa deu de aproveitável:
- **Page Previews da Wikipédia**: sem contorno; sombra em camadas fazendo o trabalho
  de separação; e — o detalhe mais valioso — **o gatilho é destacado enquanto o
  cartão está aberto**, o que ancora visualmente sem depender de um bico.
- **Tufte / sidenotes do gwern**: a nota pertence à margem, não flutua sobre o texto.
  Não adotado literalmente (perderia a demonstração do tether, que é o objeto do
  experimento), mas informou a decisão de deixar o cartão **mais claro que o papel**
  — ele está *sobre* a página, então tem que receber luz, não sombra.

O que ficou: fundo `#fbf7ec` (mais claro que o papel), **sem borda**, sombra em três
camadas (contato curta + difusa longa), raio **assimétrico** (`3px 14px 14px 14px`),
e uma **aba de dicionário** — barra de 4px na cor do verbete na borda de ataque.

**Por que aba e não bico.** Um bico é o que a literatura de popover recomenda, e foi
a primeira tentativa. Mas com `position-try-fallbacks: flip-block, flip-inline`, o
cartão pode nascer acima ou ao lado do termo, e **não existe forma em CSS de saber
que um fallback de posição foi aplicado** para mover o bico junto — `@position-try`
só aceita propriedades de inset/margem/tamanho, não custom properties. Um bico
apontando para o lado errado é pior que nenhum bico. A aba é indiferente à direção,
e tem uma referência editorial melhor (o thumb-index de dicionário impresso) que um
balão de tooltip.

O destaque do gatilho foi feito com **`:has()` puro**:
`body:has(#g-boafe:popover-open) [popovertarget="g-boafe"]{ … }`. A peça continua com
zero JS. Confirmado funcionando por captura de tela e por `getComputedStyle`.
Nota de método: `getComputedStyle` lido no **mesmo tick** do `.click()` ainda devolve
o estado antigo do `:has()` — leia depois de um `setTimeout`, ou você "descobre" que
a regra não funciona quando ela funciona.

## Usucapião: o verde saiu do chão e virou tinta

O dono não odiava a paleta sage/verde-oliva, mas não estava convencido. A releitura:
**o verde estava no lugar errado**. Como campo de fundo (`--ground:#d9dcc3`), ele
lia como "paisagem" e ficava opaco — e, pior, não dizia nada sobre o assunto. Mas
"posse que se converte em domínio pelo tempo" **é oxidação**: o verdete é literalmente
cobre reagindo com o tempo. Então o verde tem lugar; só não é o chão.

Mudou para: **chão de calcário claro** (`#e6ded4`, quente-neutro), com o **verdete
mais escuro e mais frio** (`#4f7d63` → `#2f6b58`) promovido a tinta — é a cor da
videira, dos marcadores de estágio, dos anéis de ano. Cobre e vermelhão de limite
ficaram como estavam. Tinta neutralizada (`#2c3122` → `#2b2723`: o preto era
esverdeado também).

Checagem de vizinhança, que foi o que mais restringiu a escolha: chão quente + acento
frio separa a peça do dossiê (chão quente + acentos quentes) e da bifurcação (chão
frio + acentos mistos). Uma direção de "linho + vermelhão de registro cadastral" foi
descartada justamente por colidir de frente com o mundo do dossiê, e "creme +
terracota" está proibido pela própria entrada de 2026-09-05 acima.

## Passe de celular — o que estava de fato quebrado

Além do `viewport` ausente (a causa maior, acima), com viewport de 390×844 real:

- **`.lab-home` colidia com o conteúdo** nas quatro peças. Ele é `position:fixed` em
  `top:16px; left:16px`, e no celular a coluna de texto passa a ocupar toda a largura
  — não sobra margem para ele flutuar. Ficava por cima do h1 e dos rótulos de passo.
  Corrigido nas quatro: abaixo de 720px ele vira `position:absolute` e rola junto.
- **A tabela comparativa da bifurcação era inutilizável.** Tinha `min-width:620px`
  dentro de um `.tbl-wrap{overflow-x:auto}` — tecnicamente não estourava o layout,
  mas em 390px o leitor via a coluna de critério e metade do "difuso", sem nenhuma
  pista de que dava para arrastar. Abaixo de 720px virou lista empilhada, com cada
  via ganhando rótulo próprio; continua sendo uma `<table>` real na árvore de
  acessibilidade (o `thead` é escondido visualmente, não removido).
- **O usucapião escondia a videira no celular** (`@media (max-width:640px){ .vine,
  .stage::after{ display:none } }`). Era uma decisão defensável — os elementos
  estavam em `left:-6.4vw`, fora da tela — mas o efeito era que **o motivo central da
  peça sumia justamente no aparelho em que ela mais é lida**. Em vez de esconder, a
  videira foi trazida para dentro: vão de 34px à esquerda, cartões recuados.
- **Auditoria do padrão**: a resposta à pergunta "isso está aplicado de forma
  consistente?" é **não**. O dossiê tinha um `@media (max-width:640px)`, o usucapião
  também, o glossário e a bifurcação praticamente nada. Não havia um passe de
  celular; havia remendos pontuais por peça.

## Em aberto depois desta rodada

- **A bifurcação ganhou um ramo `prefers-color-scheme: dark`** em algum momento, o
  que contraria a regra declarada de que cada peça se compromete com **um** mundo
  visual. Não foi mexido nesta rodada (não estava no escopo e o modo escuro está
  bem-resolvido), mas ou a regra muda ou a peça muda — hoje as duas coisas estão
  escritas e se contradizem.
- **O `--card` do glossário virou variável morta** depois da troca para `--slip`.
  Deixado no arquivo de propósito, para o caso de o dono querer comparar; se ficar,
  vira sujeira.
- **Bico direcional em popover ancorado continua sem solução limpa** enquanto
  `@position-try` não puder setar custom properties. Vale reconferir quando a
  especificação de anchor positioning andar.
- **A `contain` range depende do sujeito ser mais alto que a viewport.** Nesta peça
  a `.struct` é alta porque os passos usam `svh`, então escala junto com a janela.
  Numa peça com passos de altura fixa, uma janela muito alta poderia degenerar a
  faixa. Não testado; anotado antes de virar bug.

## 2026-09-05 — the homepage redesign itself was slop, caught by the owner not by review

The homepage rebuild in the entry above ("mesa de luz," dark slate hero) got shipped
after passing a real QA pass — doctype/viewport confirmed, mobile screenshot checked,
tile previews verified to render — and it was still wrong. The owner's reaction,
verbatim: "no I hate that main loading screen... it looks like slop now."

**What was actually wrong, once looked at with fresh eyes instead of defended**: near-black
background, an oversized bold grotesque headline, thin vertical grid-line texture — this
is *exactly* the generic AI-hero pattern this whole project's design guidance warns
against, just in dark mode instead of the cream-and-terracotta light-mode version already
named as a cliché. It didn't fail any functional check. It failed a check nobody had been
running: **does this still feel like the same object as the rest of the site, or does it
read as a different, unrelated product glued onto the front of it?** The four experiment
pages all commit hard to one crafted material world each (paper, ink, wax, contour lines).
The homepage, meant to be the frame around all four, was instead built as a generic dark
dev-tool landing page — it didn't even share a typeface family with anything below it.

**Fixed** by moving the hub to the same warm-paper/graphite-ink language as the pieces —
plates now read as physical index cards on paper, not glowing tiles floating in a void —
while keeping what was genuinely good (the hand-drawn per-piece SVG preview inside each
tile, the grid layout, the colophon linking to the notebook and repo).

**The actual lesson**: "verify it works" (doctype, viewport, mobile screenshot, computed
styles) and "verify it doesn't feel generic" are two different checks, and passing the
first one provides zero evidence about the second. A visual-craft QA pass needs an
explicit step that asks "would this read as generated by any AI system asked for a
homepage, with no other context" — not just "does the thing I built do what I said it
does." Worth remembering next time a piece is reviewed only functionally before shipping.

## 2026-09-05 — homepage, terceira tentativa: diário de bordo (não é resumo)

Escrito **durante** o trabalho, na ordem em que as coisas aconteceram, inclusive os
becos sem saída e as versões que foram para o lixo. O pedido explícito do dono foi
esse: "o caminho que você percorre vale mais que a direção final". Então fica messy.
Um resumo limpo do resultado estaria mentindo sobre como isso foi feito — a primeira
versão *deste próprio registro* era um resumo limpo, e foi reescrita por isso.

Contexto de entrada: duas homepages já rejeitadas. A nº 1 (hero quase-preto, manchete
grotesca gigante, grade vertical fina) e a nº 2 (gabinete de curiosidades, nogueira e
latão), essa última com o veredito "não consigo enfatizar o quanto isso parece slop".

---

### Passo 0 — medir antes de opinar

Antes de escrever uma linha, servi o site local e capturei o `index.html` em 1440×900,
mais as quatro peças, para ter referência. **Isso já pagou**: o "veio de madeira" da
tentativa 2, na captura em tamanho real, era indistinguível de preto chapado. O que
aparecia era um retângulo marrom-escuro liso com cartões claros. A textura existia no
CSS e não existia na tela.

Comparando com a captura do dossiê lado a lado, a diferença ficou óbvia e é a lição
mais transferível do dia: **o dossiê tem uma trama de pontinhos em passo discreto,
perceptível a olho nu.** Não é um gradiente sutil, é um padrão que dá pra ver. Toda
textura que "some" é textura que não foi feita.

Segunda coisa que só apareceu porque olhei as quatro juntas: **elas já têm uma gramática
de casa**, e ninguém tinha escrito isso em lugar nenhum. Chão de papel quente, tinta
grafite, Newsreader ou Fraunces no display, Courier Prime nos rótulos, emblema desenhado
acima do título, olho tipográfico centralizado. As duas homepages rejeitadas quebravam
todos esses itens de uma vez.

### Passo 1 — beco sem saída nº 1: "moldura neutra" (construída inteira, e jogada fora)

Primeira hipótese, com pesquisa de portfólio/galeria por trás ("restraint reads as
confidence", "a variedade lê como versatilidade em vez de dispersão", moldura quieta e
o trabalho carrega a cor). Construí a página inteira assim: papel morno neutro —
escolhido como a **média** dos quatro chãos das peças, para pertencer às quatro sem ser
nenhuma —, marca de registro riso, filete fora de registro, cartões com aba de polegar.

**Morreu por correção do dono, não por defeito próprio.** A lógica de portfólio estava
certa em abstrato e errada para este projeto: a homepage não deve recuar, deve ter um
mundo tão comprometido quanto as quatro peças.

O que **sobreviveu** desse beco e foi parar na versão final, e por isso o beco não foi
desperdício:
- a ideia da **marca de registro** em três chapas fora de alinhamento;
- a leitura de que as três faces da casa (Fraunces / Crimson Pro / Courier Prime) devem
  ser reusadas, não substituídas por três inéditas — a tentativa 2 tinha inventado
  Bricolage/Literata/Martian e "não compartilhava nem a família tipográfica com nada
  abaixo dela" já estava anotado aqui como defeito;
- a lição do glossário de que **o cartão está *sobre* a página, então recebe luz** —
  aplicada depois às provas.

### Passo 2 — beco sem saída nº 2: folha de prova de gráfica

Com "comprometa-se com um material" na mão, fui para **folha de prova de impressão**:
marcas de corte, barra de cores, carimbo PROVA, papel de gramatura suja. Cheguei a
pesquisar convenções reais de riso (misregistro de 1–3mm tratado como estética, marcas
de registro servindo também de corte).

Estava a meio caminho de escrever quando veio a segunda correção, e ela reformula o
problema inteiro: **o meio compartilhado do site é papel**, não "analógico em geral".
A folha de prova por acaso *é* papel, então parte do trabalho se salvou — mas o
raciocínio estava errado, e teria acertado por sorte.

**A frase que resolve o projeto**: papel-heliográfico é papel. A bifurcação, que tem o
mundo mais escuro das quatro, não é a exceção da regra do papel — é a prova dela.
"Escuro" e "técnico" são sabores de papel, não outro material. Isso reclassifica o
fracasso da tentativa 2: não foi só o veio invisível, foi que **madeira nunca esteve no
vocabulário**, e um gabinete de nogueira perfeitamente executado teria sido rejeitado
do mesmo jeito.

### Passo 3 — candidatos considerados e descartados (com o motivo)

Anotando os descartes porque o motivo de cada um é reutilizável:

- **Kraft / pasta de papelão.** Papelão é papel, tem fibra visível de verdade, e é o
  objeto que literalmente guarda folhas soltas. **Descartado por risco de leitura**:
  marrom médio, logo depois de uma rejeição por madeira, ia reler como madeira de novo.
  O material estava certo e o *timing* estava errado — vale guardar para outra hora.
- **Quadro de cortiça com as peças pregadas.** Cortiça não é papel. Fora.
- **Cartão de passe-partout de museu.** Papel, é literalmente feito para apresentar
  obras separadas, e tem um detalhe lindo (o miolo branco aparecendo no bisel). Perdeu
  por legibilidade: exige que o leitor reconheça um objeto de nicho.
- **Cianótipo / papel-planta azul da Prússia.** Espetacular, inconfundivelmente papel,
  e o dono citou blueprint. **Descartado**: a tentativa 1 morreu exatamente por "textura
  de grade azulada". Voltar para lá seria repetir o erro com melhor acabamento.

**Escolhido**: prancha de montagem de **papel técnico escuro**, ardósia fria `#22303c`.
Azulada de propósito — é a decisão de cor mais deliberada da página, e existe só para
tornar impossível a leitura "madeira". As quatro peças ficam presas com fita nela.

Um ganho não previsto dessa escolha: como as provas são folhas claras **coladas** numa
prancha escura, com fita e sombra, elas não caem no defeito de "cartões claros flutuando
num vazio escuro" que era o sintoma das tentativas 1 e 2. É o mesmo contraste, mas com
explicação física.

### Passo 4 — primeira montagem, e o que a captura mostrou

Empilhamento de três folhas, fita com pontas irregulares em `clip-path`, borda inferior
rasgada, carimbo, marca-texto, marca de registro. Capturei em 1440×900.

Melhorou muito. Mas com olhar frio, três coisas:

1. **O marca-texto quebrou em duas linhas e virou duas etiquetas amarelas com cantos.**
   Culpa do `box-decoration-break: clone`: cada fragmento ganha suas próprias pontas
   suaves, então lê como dois rótulos, não como um traço de caneta. Caneta marca-texto
   não faz isso. `white-space: nowrap` no trecho destacado é obrigatório, não estético.
2. **A fibra da prancha estava fechando em grade.** Quatro campos de pontinhos em
   43/61/53/31px com alfa alto. De longe: grade. Ou seja, eu tinha reinventado sozinho
   o defeito da tentativa 1, por outro caminho.
3. **Composição vazia à direita** e um buraco vertical grande antes da faixa de seção.

### Passo 5 — o ajuste pequeno com efeito grande

Este é o achado que eu não teria previsto, e é exatamente o tipo de coisa que o dono
pediu para registrar.

Para consertar a grade, o instinto é **aumentar** a irregularidade dos pontos. Não
funciona: mexer nos passos só troca uma grade por outra. O que funcionou foi um par de
mexidas em direções opostas:

- **baixar** o alfa dos campos de pontinhos (`.30 → .19`) e trocar os passos por pares
  primos entre si (37/41, 59/53, 83/71, 29/31);
- **subir** o `feTurbulence` de `opacity:.2` para `.3` em `mix-blend-mode: screen`.

Isoladamente cada uma piora: só baixar o alfa dá uma prancha lisa e morta; só subir o
ruído dá sujeira por cima de uma grade ainda visível. Juntas, a leitura muda de
categoria — vira **fibra**. A regra que sai daí: *padrão regular carrega a estrutura,
ruído verdadeiro carrega a credibilidade, e quem tem que dominar é o ruído.* Quando
uma textura lê como grade, o conserto quase nunca é mexer na grade; é rebaixar a grade e
promover o ruído.

Efeito parecido, mesma lógica, no papel creme: `.17` em passo 7px lia como papel
quadriculado; `.115` em 6px passou a ler como grão de papel. **Menor e mais fraco leu
como mais material**, o que é contraintuitivo o bastante para ficar anotado.

### Passo 6 — a ficha de tintas: conserta composição, quebra manchete

Para o vazio à direita, criei uma **ficha de tintas** (quarta camada de papel, com sua
própria fita e sombra, listando as quatro cores das peças). Ideia boa: acrescenta
empilhamento, que é o que se quer, e dá a chave de cor antes de o leitor chegar nas
peças.

Captura seguinte: **a ficha cobria a palavra "vira" da manchete.** Um problema de
composição consertado criando um problema de legibilidade — que é o modo de falha
clássico de colagem, e vale ter na cabeça: em layout de papel empilhado, todo elemento
novo é um oclusor em potencial.

Movida para o canto superior direito, **transbordando a borda da folha**. Resolveu os
dois de uma vez e, de brinde, ficou melhor do que a posição original: três camadas de
papel se sobrepõem num canto só, então a profundidade se lê num ponto de foco em vez de
espalhada. Tirei a fita `t-b` que estava ali, porque a ficha trouxe a dela.

### Passo 7 — duas coisas que só a captura pega

- **Celular 390px: o carimbo caía por cima das últimas linhas do parágrafo.** No desktop
  ele mora numa área vazia à direita; no celular essa área não existe. Abaixo de 720px
  ele entra no fluxo, encostado à direita, ainda torto.
- **A janela do glossário sangrava no cartão.** O papel daquela peça (`#efe9da`) é quase
  idêntico ao papel da prova (`#efe7d3`), e a hairline em `.2` não separava. Subiu para
  `.34` mais uma sombra interna de 2px. Mudança minúscula, efeito grande: as quatro
  janelas passaram a ler como **impressos montados** em vez de manchas no cartão.

### Notas técnicas que custaram tempo

- **`clip-path` anula `box-shadow`.** A folha rasgada não aceita sombra própria; ela tem
  que vir de `filter: drop-shadow()` num invólucro, que aí sim segue a silhueta
  recortada. Descoberto na pesquisa antes de bater no bug, mas por pouco.
- **Campos de pontinhos com fator comum entre os passos fecham em grade.** Ver passo 5.
- **`translate` como propriedade própria, não dentro de `transform`.** Cada prova tem
  uma inclinação em `transform: rotate()`; a animação de entrada usa `translate:`, então
  as duas compõem sem se sobrescrever. Mesma armadilha já anotada neste caderno para
  parallax.

### Verificação

Receita do CDP headless deste caderno (servidor local + `--headless=new` +
`Page.captureScreenshot`), com `document.hidden === false` confirmado — sem isso as
scroll-timelines mentem. Capturas em 1440×900 e 390×844, mais **recorte a 4x** da
textura, que é o único jeito honesto de responder "isso lê como fibra ou como grade?".
`prefers-reduced-motion: reduce` emulado por `Emulation.setEmulatedMedia`: as quatro
provas ficam em `opacity: 1` e mantêm a inclinação — estado final estático correto.

### Em aberto, honestamente

- **Só testado em Chromium.** `mix-blend-mode: multiply` em grupos SVG e a dupla
  `clip-path` + `drop-shadow` merecem uma olhada no Safari antes de virar produção.
- **A fibra da prancha é a parte mais "simulação" da página**, e é significativo que
  tenha sido justamente a que mais brigou comigo. O briefing diz estilizar, não
  reproduzir. Do jeito que está, funciona e lê como ilustração digital de papel, não
  como foto — mas se algum dia essa página for reaberta, esse é o primeiro lugar onde eu
  tentaria **menos simulação e mais forma gráfica chapada**, e provavelmente ficaria
  melhor e mais barato.
- **O rasgo é um `clip-path` fixo**: sempre o mesmo rasgo, em qualquer largura. Ninguém
  vai notar numa página só. Numa família de páginas, vai.
- **Kraft/papelão continua um material não usado** e sem defeito conhecido — só foi
  descartado pelo timing da rejeição por madeira.

### Candidatos a princípio de casa (para o "bíblia de estilo" futuro)

Não são regras fechadas, são o que este passe sustenta:

1. **O meio é papel**, em variantes livres. Escuro e técnico é um sabor de papel.
2. **Textura que não aparece numa captura em tamanho real não existe.** Padrão
   perceptível em passo discreto, não gradiente sutil.
3. **Ruído verdadeiro domina padrão regular**, ou a textura vira grade.
4. **Estilizar, não reproduzir.** As peças são ilustrações digitais *de* papel e cera,
   não fotos.
5. **Reusar as faces da casa** (Fraunces / Newsreader / Crimson Pro / Courier Prime) em
   vez de inventar um trio novo por página.
6. **Papel empilha, recebe fita, carimbo, marca-texto e rasga.** Esse é o kit expressivo
   e ele deve aparecer em escala exagerada, não discreta.
7. **Verificação visual é uma segunda checagem, separada da funcional.** "Funciona" e
   "não parece genérico" são perguntas diferentes, e passar na primeira não diz nada
   sobre a segunda.

## 2026-09-05 — homepage, rodada 4: TRÊS alternativas em paralelo (diário, ao vivo)

Pedido do dono, literal: *"try fucking around... I don't want to give specific criticism
because I don't want to give you a specific direction yet."* Ou seja: **não convergir**.
Saída = três páginas completas e genuinamente divergentes (`index-alt-a/b/c.html`), com a
`index.html` atual **intocada**. Este bloco é escrito durante o trabalho, na ordem.

### Passo 0 — capturar a versão viva e ler friamente

Servi local + CDP headless (`document.hidden === false` confirmado) e capturei a
`index.html` atual em 1440×900 antes de escrever qualquer linha.

Leitura fria, e é o achado que define esta rodada: **a tentativa 3 é a tentativa 1 com
outra roupa.** O esqueleto é idêntico — um bloco-herói grande e centrado no topo, uma
faixa de seção, e uma grade 2×2 de cartões claros embaixo. Trocar "hero escuro + grade"
por "folha de papel + grade" mudou o material e **não mudou a composição**. É provável
que seja exatamente isso que o dono não consegue nomear: ele já viu essa página três
vezes, sempre com a mesma planta baixa.

Segunda observação da captura: a "fibra" da prancha, em tamanho real, ainda lê como uma
trama de pontinhos regular sobre azul-ardósia liso. O passo 5 do diário anterior melhorou,
mas não resolveu — de longe continua sendo *padrão*, não *matéria*.

**Regra autoimposta para as três alternativas:** nenhuma delas pode ter a silhueta
"bloco de título no topo + grade de cards embaixo". Se a planta baixa não muda, o
material novo não vale nada.

### As três apostas (escolhidas para divergirem entre si, não para agradarem)

- **A — mural de cartazes rasgados.** Colagem sangrando na tela inteira, quatro cartazes
  grandes em tinta chapada saturada, sobrepostos e tortos, papel colado sobre papel.
  Máximo de barulho, sem grade.
- **B — livro de índice aberto.** Página dupla de papel vergê com calha central, pauta,
  filetes vermelhos. As quatro peças viram **linhas de uma tabela manuscrita**, não
  cards. Quieto, arquivístico, quase sem cor.
- **C — papel recortado chapado.** A resposta ao item em aberto do diário anterior
  (*"menos simulação e mais forma gráfica chapada"*): formas grandes de papel cortado,
  sombra dura sem blur, retícula grossa como única textura, muito vazio.

### A — mural de cartazes: o que a captura pegou (três defeitos, todos invisíveis no código)

1. **O misregistro da manchete duplicou o texto.** A técnica é uma cópia da manchete em
   vermelhão, 3px fora, em `multiply`. A cópia é `position:absolute` — e o `h1` **não era**
   `position:relative`, então o bloco de contenção virou o `.title`, que é muito mais largo:
   a cópia não quebrou nas mesmas linhas do original e a página exibiu *"Material denso vira
   interface. / vira interface."*, em preto e vermelho. Uma linha de CSS (`h1{position:relative}`)
   e um erro que **só existe na tela** — o HTML está correto e o CSS "parece" certo.
   Regra: sobre-impressão fora de registro exige que a cópia herde a **mesma caixa**, não só
   a mesma string.
2. **Vão morto de ~200px entre a manchete e os cartazes.** Estava lendo como dois blocos
   empilhados, ou seja, exatamente a planta baixa que esta alternativa existe para evitar.
   Correção: `margin-top` negativo na lauda no desktop, para ela **encavalar** a metade
   vazia da faixa do título. Colagem é sobreposição; se nada se sobrepõe, é grade.
3. **Cartaz vizinho comendo o título do outro.** Com sobreposição de uma coluna inteira
   (~107px) e padding de 26px, dava para ler *"erra Muda de / o"* na peça 02. Duas correções
   combinadas: reduzir a sobreposição para ~70px **e** dar `padding-left` de 88px a quem
   fica por baixo. Anotação transferível: **numa colagem, sobreposição e padding são a mesma
   variável** — quem aumenta uma tem que aumentar a outra, ou perde texto.

**Textura, verificada em recorte 3×:** o chão de jornal passou. O que resolveu foi a mesma
regra do diário anterior aplicada na direção oposta ao instinto — os campos de pontinhos
foram de passos 43/67/89px para 13/19/23/31px com alfa **caído pela metade**, e o
`feTurbulence` subiu de .34 para .5 em `multiply`. Pontinho grande e forte = bolinha; ponto
pequeno e fraco + ruído forte = fibra.

A **retícula do cartaz** (4.5px, `screen`, sobre tinta chapada) aparece sem esforço em
1440px e é o que impede a tinta de ler como `background-color`. É a técnica mais barata da
página inteira e provavelmente vale para qualquer peça futura com campo de cor chapado.

Verificado também: 390×844 (cartazes empilhados com inclinações menores, sem sobreposição)
e `prefers-reduced-motion: reduce` (estado final estático, inclinações mantidas).

### B — livro de registro: a textura que finalmente não é grade, e a única correção estrutural

Esta foi a mais fácil de acertar de primeira, e vale entender por quê: **quando a
composição já é a metáfora, a textura tem menos trabalho a fazer.** A calha da
encadernação com sombra, o filete vermelho de margem, o cabeçalho de duas réguas e as
abas de polegar na borda direita já dizem "livro" antes de qualquer fibra aparecer. Nas
tentativas anteriores a textura carregava sozinha a promessa de material — e era por isso
que ela tinha que ser tão forte, e por isso brigava tanto.

**A correção de textura, mesmo assim, foi a de sempre e na mesma direção.** A primeira
captura mostrava as vergaturas (3px) cruzando com os pontusais (27px) e fechando numa
**trama xadrez visível** — de novo a grade, pela terceira vez neste caderno, por um
terceiro caminho. Correção: vergaturas de `.075` → `.038`, pontusais de `.13` → `.06`,
`feTurbulence` de `.4` → `.56`. **Terceira confirmação independente da regra do passo 5
do diário anterior:** quando lê como grade, rebaixe o padrão e promova o ruído.

**O que salvou o papel foi o foxing, não a fibra.** As manchas ferruginosas estavam em
8–18px e alfa .1–.16, ou seja, invisíveis em 1440px. Dobradas de tamanho (15–32px) e
subidas para .18–.26, viraram o elemento mais legível da página — e são o que faz o papel
ler como **envelhecido** em vez de bege. Anotação para a bíblia de estilo: numa peça de
papel, uma mancha grande e irregular vale mais que qualquer trama regular, e é mais barata.

**Único defeito real de composição, e só apareceu em 390px:** a linha do registro é uma
grade `108px 1fr 168px` e, no celular, virava `76px 1fr` — o que deixava o parágrafo com
~28ch numa tira estreita ao lado do espécime. Corrigido para bloco (espécime vira selo de
96px acima do texto). Junto com isso, **um bug de cascata que a captura pegou e o código
não denunciava**: a regra `@media (max-width:639px){ .specimen{ width:96px } }` estava
escrita ANTES da regra genérica `.specimen{ width:100% }` no arquivo, e perdia o empate
de especificidade. Resolvido subindo o seletor para `.entry .specimen`. Vale a nota geral:
**bloco de media query escrito antes da regra base não vence por ser media query** —
media query não adiciona especificidade nenhuma.

**Detalhe que funcionou melhor do que eu esperava:** o hover. Não levanta cartão (livro
não levanta) — passa marca-texto na linha inteira e acende um "bico de pena" na margem
esquerda, na cor da peça. O gesto certo para o objeto certo, e é mais barato que o
`translateY` + sombra que todo card faz.

### C — papel recortado / sanfona: cobrando a promessa deixada em aberto

Esta alternativa não é uma ideia nova, é uma **dívida do diário anterior sendo paga**. A
seção "em aberto, honestamente" da tentativa 3 diz, com todas as letras, que a fibra da
prancha era a parte mais "simulação" da página, que foi justamente a que mais brigou, e
que numa próxima vez o certo seria *menos simulação e mais forma gráfica chapada*. Então
esta página tem uma regra única e severa: **nenhuma textura de fibra, nenhuma sombra com
blur, nenhum gradiente de iluminação.** Papel aqui é recorte: silhueta, cor chapada, e
sombra dura de deslocamento sólido.

**O que confirma a hipótese:** custou muito menos. O arquivo tem ~14 KB contra ~22 KB das
outras duas, o CSS não tem uma única pilha de sete `radial-gradient`, e a primeira captura
já estava 80% certa — enquanto A e B precisaram de três rodadas de ajuste de textura cada.
Forma chapada é mais barata *e* mais robusta, exatamente como o diário suspeitava.

**Duas decisões que só apareceram na hora de executar:**

- **O marca-texto teve que mudar de espécie.** As outras duas páginas usam o traço de
  caneta em `mix-blend-mode: multiply`, que é a técnica de casa. Aqui ela estaria errada:
  numa página em que nada é translúcido, um traço translúcido é um corpo estranho. Virou
  uma **tira de papel amarelo chapada por baixo da palavra** (`::before` com `z-index:-1`).
  Anotação: *a técnica de casa é subordinada ao material da peça, não o contrário.*
- **O furo é vazado de verdade, com `mask-image`, não pintado com a cor do fundo.** Parece
  preciosismo, e não é: se o painel se move no hover, um círculo pintado se move junto e
  denuncia a farsa; um furo de máscara continua mostrando o fundo, que fica parado. Custo
  idêntico, honestidade diferente.

**Correções que a captura pegou:**
1. **A diagonal do segundo papel não lia como corte.** `--ground-2` estava a 5% do
   `--ground` e a "sombra" era um `::after` com `clip-path` próprio — invisível. Duas
   correções: contraste maior entre os dois papéis, e a sombra passou a ser
   `filter: drop-shadow(0 9px 0 …)` **com blur zero**, no próprio elemento recortado
   (`clip-path` anula `box-shadow` — nota já registrada neste caderno, agora usada em vez
   de redescoberta).
2. **Em 390px o disco vermelho sangrava por cima do kicker**, deixando texto escuro sobre
   vermelho. Disco empurrado para fora do canto e a cauda do kicker escondida abaixo de
   719px.

**Ressalva honesta desta alternativa, que o dono deve saber ao olhar:** a retícula de 6px
é, num recorte 3×, um **reticulado perfeitamente regular** — ou seja, contraria a regra
nº 3 da casa ("ruído verdadeiro domina padrão regular"). Aqui isso é deliberado: uma
retícula de impressão *é* regular, e a peça inteira assume forma gráfica em vez de
simulação. Mas é exatamente o tipo de decisão que pode ser lida como "de novo a grade".
Fica registrado como escolha consciente, não como descuido — e se o dono reagir a isso,
a correção é meia linha de `feTurbulence`, não um redesenho.

### Fechamento da rodada 4

Três arquivos entregues, todos completos e funcionais, `index.html` **intocada**:

| | composição | humor | material |
|---|---|---|---|
| **A** `index-alt-a.html` | colagem sobreposta, sem grade | barulhento, de rua | jornal + cartaz de tinta chapada |
| **B** `index-alt-b.html` | página dupla, tabela de registro | quieto, arquivístico | papel vergê com foxing |
| **C** `index-alt-c.html` | sanfona de quatro painéis | seco, gráfico, muito vazio | papel recortado chapado |

Verificação em todas as três: CDP headless com `document.hidden === false`, capturas em
1440×900 e 390×844, recorte 3× da textura, e `prefers-reduced-motion: reduce` emulado
(estado final estático em todas).

**O que esta rodada ensinou, independente de qual delas o dono escolher (ou nenhuma):**
a variável que estava travada nas três tentativas anteriores não era o material — era a
**planta baixa**. As três primeiras homepages tinham a mesma silhueta com roupas
diferentes, e trocar a roupa nunca resolveu. Assim que a composição mudou de verdade
(colagem, página dupla, sanfona), o material passou a ter onde se apoiar e cada escolha de
textura ficou mais fácil, não mais difícil. Se houver uma quarta rodada, começar pela
composição, não pela paleta.

## 2026-09-05 — owner's live reaction to alt-A (mural), before seeing B or C

Real-time critique from the owner looking at `index-alt-a.html`, worth keeping close to
verbatim since the shape of the feedback matters as much as the content.

**Real bug, flagged precisely**: the highlighter mark over "veículo descartável" doesn't
fully cover the last word — ends short. Same shape of mistake as an earlier highlighter
bug in this project (a mark sized to a wrapping box instead of the actual text run it's
meant to cover) — check that pattern specifically whenever a highlight/underline element
is involved, it's recurred more than once now.

**A real physical-behavior note, offered as observation not demand**: the current
highlighter renders with soft/blurred edges left-right but hard/straight edges top-bottom.
A real highlighter mark does the opposite — soft rounded caps at both ends (where the felt
tip lifts off the page), comparatively crisp top/bottom (the tip has a fixed width). Worth
fixing generally: whenever imitating a physical marking tool, work out which edges of the
real object are soft vs. hard before choosing where to blur.

**The important one — a new, named failure mode, distinct from the previous two**:
every individual technique in alt-A was praised specifically and by name — paper glued on
paper (layered torn sheets), tape, a dotted ruler-drawn line ("makes me think someone went
with a ruler"), textured numerals, reusing each piece's *own* diagram as its tile's
illustration, the underline treatment. All confirmed as real, on-brand wins worth keeping
in the permanent toolkit regardless of what happens to alt-A as a whole. **But the owner's
read of the composition as a whole was "pastiche," "collage," "eclectic," and — the most
useful single image — "university campus bulletin board, pamphlets stacked on pamphlets."**

This is a *third*, different failure mode from the first two homepage rounds:
- Round 1 (dark hero): wrong register entirely — generic, no material at all.
- Round 2 (wood cabinet): right *ambition*, wrong *material* — skeuomorphic effort spent
  on something outside the project's medium.
- Alt-A: right material, right individual techniques, **but no unifying restraint** —
  a page can execute every technique correctly and still fail because it reads as a
  demo reel of ideas rather than one considered gesture. Craft at the atomic level does
  not add up to coherence at the composition level automatically; something else (a
  dominant single idea, a hierarchy among the techniques, restraint about how many
  "voices" appear on one page) has to hold the individual wins together on purpose.

Not yet resolved: whether alt-B or alt-C avoid this, and whether the fix for a future
attempt is "use fewer of these techniques per page" or "find the one organizing idea that
lets several of them coexist without reading as a pile." Owner explicitly paused feedback
here to look at B and C before drawing conclusions — entry to be continued.
