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
