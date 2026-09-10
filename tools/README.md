# Course builder

`build_course.py` converts the selected Markdown entries in a JSON manifest
into a static reading course. The source guide is read-only; the builder does
not modify the source vault or summarize its chapters. It preserves the full
selected guide in chapter order, while recording declared source-specific
corrections and removed operational frontmatter in the private build report.

Run it from the site repository with a portable manifest and private source
root:

```sh
python3 tools/build_course.py tools/teoria.config.json \
  --source-root "/path/to/private/course/luna_output" \
  --output-dir courses/teoria-do-delito \
  --report-path "/path/to/private/reports/teoria-build-report.json"
```

The committed manifest contains source-relative filenames. Keep the source
root and report path outside the public repository when they contain local
machine details. The generated `catalogue.json`, `search-index.json`, and
`provenance.json` contain public source names, hashes, counts, and logged
transformations, without absolute paths or frontmatter secrets.

The builder uses only the Python standard library plus Mermaid CLI (`mmdc`)
for diagram rendering. The verified local CLI is Mermaid `11.16.0`; its build
environment also needs the Puppeteer `chrome-headless-shell` runtime matching
the installed CLI (the verified local runtime is `152.0.7977.54`). Browser
runtime dependencies are build-time only: visitors load the committed SVG
assets and do not need Mermaid, Puppeteer, or JavaScript diagram compilation.

Supported source conventions include YAML frontmatter, headings with unique
permalinks, fenced code, tables, footnotes, nested ordered/unordered lists,
Obsidian INFO/NOTE/CAUTION/EXAMPLE callouts, local Markdown links, and
`{{mermaid:diagrams/name.mmd}}` markers. Mermaid source is compiled into local
SVG assets and accompanied by an accessible collapsed relationship list.

When a course index contains `<!-- COURSE_CONTENTS_START -->` and
`<!-- COURSE_CONTENTS_END -->`, the builder replaces only the content between
those markers, preserving the surrounding template. The build fails on
unresolved local links, diagram markers, raw wikilinks, malformed `****`
artifacts, or an incorrect count for a declared source-specific correction.

## Explicit generated/public output mapping

Each unit normally writes `<id>.html`. A unit may explicitly set
`generated_output` when the generated reading must be kept under a different
filename, and `public_output` when catalogue, search, source links, and
pagination should point to an authored public page. The builder does not scan
for authored files and does not rewrite or replace them. For example, the
Teoria do Delito manifest maps unit 08 to `unidade-08-original.html` for the
generated, unabridged reading while retaining `unidade-08.html` as the public
lesson route.

This mapping is a provenance transformation: the original page records the
source reading and the generated page's report/hash, while the authored page
is the public teaching surface. The provenance and source-fidelity verifier
must therefore compare the original generated output against its declared
source; it cannot infer that the authored primary page is source-faithful from
the public route alone. Keep the publication mapping in the manifest's
`editorial` metadata so a generic rebuild carries it into `provenance.json`.

After the generic course build, run `python3 tools/build_unit08.py` from the
repository root. It renders the authored lesson from `tools/editorial/unit08.json`
and the diagram template, refreshes asset references, and records hashes of its
editorial input, renderer and output in course provenance. The original reading
is generated separately; do not replace it with the authored adaptation.
