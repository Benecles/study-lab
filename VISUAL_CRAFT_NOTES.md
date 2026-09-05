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
