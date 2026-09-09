#!/usr/bin/env python3
"""Build a static, semantic course reader from selected Markdown sources.

The builder intentionally has no third party dependency: its small Markdown
renderer covers the source conventions used by the study packs while retaining
the source text and reporting every transformation.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
    return re.sub(r"[-\s]+", "-", value) or "section"


def render_list(lines: list[str], start: int, resolver, footnote_ids) -> tuple[str, int]:
    """Render one indentation level, retaining nested Markdown lists."""
    first = re.match(r"^(\s*)([-*+] |(\d+)[.] )(.*)$", lines[start])
    indent = len(first.group(1).replace("\t", "    "))
    ordered = bool(first.group(3)); tag = "ol" if ordered else "ul"
    attrs = (' start="%s"' % first.group(3)) if ordered and first.group(3) != "1" else ""
    items: list[str] = []; i = start
    while i < len(lines):
        m = re.match(r"^(\s*)([-*+] |(\d+)[.] )(.*)$", lines[i])
        if not m: break
        level = len(m.group(1).replace("\t", "    "))
        if level < indent: break
        if level > indent:
            nested, i = render_list(lines, i, resolver, footnote_ids)
            if items: items[-1] += nested
            continue
        if bool(m.group(3)) != ordered: break
        item = inline(m.group(4), resolver, footnote_ids); i += 1
        continuation = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^\s*([-*+] |\d+[.] )", lines[i]):
            if len(lines[i]) - len(lines[i].lstrip()) > indent:
                continuation.append(lines[i].strip()); i += 1
            else: break
        if continuation: item += " " + inline("\n".join(continuation), resolver, footnote_ids)
        items.append("<li>%s</li>" % item)
    return "<%s%s>%s</%s>" % (tag, attrs, "".join(items), tag), i


def read_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    if not text.startswith("---"):
        return {}, text, False
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return {}, text, False
    metadata: dict[str, Any] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            key, val = match.groups()
            val = val.strip().strip("\"'")
            if val.lower() in ("true", "false"):
                metadata[key] = val.lower() == "true"
            elif val.startswith("[") and val.endswith("]"):
                metadata[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
            else:
                metadata[key] = val
    return metadata, "\n".join(lines[end + 1:]), True


def inline(text: str, link_resolver, footnote_ids: dict[str, int]) -> str:
    # Protect code spans before applying other inline syntax.
    stash: list[str] = []
    def code(m):
        stash.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        return f"\x00{len(stash)-1}\x00"
    text = re.sub(r"`([^`]+)`", code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", lambda m: '<img alt="%s" src="%s">' % (m.group(1), html.escape(m.group(2), quote=True)), text)
    def link(m):
        label, target = m.group(1), m.group(2).strip()
        href = link_resolver(target)
        return '<a href="%s">%s</a>' % (html.escape(href, quote=True), label)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\[\^([\w-]+)\]", lambda m: '<sup class="footnote-ref"><a href="#fn-%s">%s</a></sup>' % (m.group(1), footnote_ids.get(m.group(1), m.group(1))), text)
    text = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: "<strong>%s</strong>" % (m.group(1) or m.group(2)), text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)", lambda m: "<em>%s</em>" % (m.group(1) or m.group(2)), text)
    text = re.sub(r"  \n", "<br>\n", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


def parse_table(lines: list[str], resolver, footnote_ids) -> str:
    rows = []
    for line in lines:
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return "<p>%s</p>" % inline("\n".join(lines), resolver, footnote_ids)
    head = rows[0]
    body = [r for r in rows[2:] if any(r)]
    out = ["<div class=\"table-wrap\" tabindex=\"0\" role=\"region\" aria-label=\"Tabela com rolagem horizontal\"><table><thead><tr>"]
    out += ["<th scope=\"col\">%s</th>" % inline(x, resolver, footnote_ids) for x in head]
    out += ["</tr></thead><tbody>"]
    for row in body:
        out += ["<tr>"] + ["<td>%s</td>" % inline(x, resolver, footnote_ids) for x in row] + ["</tr>"]
    return "".join(out + ["</tbody></table></div>"])


def render_markdown(text: str, resolver, diagram_resolver, transformations: list[dict[str, Any]]) -> tuple[str, list[dict[str, str]]]:
    lines = text.replace("\r\n", "\n").split("\n")
    footnotes: dict[str, str] = {}
    body: list[str] = []
    content_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\[\^([\w-]+)\]:\s*(.*)$", line)
        if m:
            value = [m.group(2)]; i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i].startswith("\t")):
                value.append(lines[i].lstrip()); i += 1
            footnotes[m.group(1)] = "\n".join(value)
        else:
            content_lines.append(line)
            i += 1
    ids = {k: i + 1 for i, k in enumerate(footnotes)}
    i = 0
    used_anchors: set[str] = set()
    while i < len(content_lines):
        line = content_lines[i]
        if not line.strip():
            i += 1; continue
        marker = re.search(r"\{\{mermaid:([^}]+)\}\}", line)
        if marker:
            path = marker.group(1).strip()
            body.append(diagram_resolver(path))
            transformations.append({"type": "diagram-marker", "source": path, "action": "svg-and-text-alternative"})
            i += 1; continue
        h = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if h:
            level, title = len(h.group(1)), h.group(2)
            anchor = slugify(re.sub(r"[`*_]", "", title))
            base = anchor; n = 2
            while anchor in used_anchors:
                anchor = f"{base}-{n}"; n += 1
            used_anchors.add(anchor)
            body.append(f'<h{level} id="{anchor}"><a class="heading-anchor" href="#{anchor}" aria-label="Permalink to {html.escape(title)}">¶</a>{inline(title, resolver, ids)}</h{level}>')
            i += 1; continue
        callout = re.match(r"^>\s*\[!([A-Za-z]+)\]\s*(.*)$", line)
        if callout:
            kind, title = callout.group(1).upper(), callout.group(2).strip() or kind.title()
            call_lines = []
            i += 1
            while i < len(content_lines) and (content_lines[i].startswith(">") or not content_lines[i].strip()):
                val = re.sub(r"^>\s?", "", content_lines[i])
                if val.strip(): call_lines.append(val)
                i += 1
            allowed = {"INFO", "NOTE", "CAUTION", "EXAMPLE"}
            css = kind.lower() if kind in allowed else "note"
            body.append('<aside class="callout callout-%s"><h3 class="callout-title">%s</h3><p>%s</p></aside>' % (css, inline(title, resolver, ids), inline("\n".join(call_lines), resolver, ids)))
            transformations.append({"type": "callout", "source": kind, "action": "semantic-aside"})
            continue
        if line.startswith("```") or line.startswith("~~~"):
            fence = line[:3]; lang = line[3:].strip(); code_lines = []; i += 1
            while i < len(content_lines) and not content_lines[i].startswith(fence):
                code_lines.append(content_lines[i]); i += 1
            if i < len(content_lines): i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            body.append("<pre><code%s>%s</code></pre>" % (cls, html.escape("\n".join(code_lines), quote=False)))
            continue
        if "|" in line and i + 1 < len(content_lines) and re.match(r"^\s*\|?\s*:?-{3,}", content_lines[i + 1]):
            table = [line, content_lines[i + 1]]; i += 2
            while i < len(content_lines) and "|" in content_lines[i] and content_lines[i].strip():
                table.append(content_lines[i]); i += 1
            body.append(parse_table(table, resolver, ids)); continue
        list_m = re.match(r"^\s*([-*+] |\d+[.] )(.*)$", line)
        if list_m:
            rendered, i = render_list(content_lines, i, resolver, ids)
            body.append(rendered); continue
        if line.startswith(">"):
            quote = []
            while i < len(content_lines) and content_lines[i].startswith(">"):
                quote.append(re.sub(r"^>\s?", "", content_lines[i])); i += 1
            body.append("<blockquote><p>%s</p></blockquote>" % inline("\n".join(quote), resolver, ids)); continue
        para = [line]; i += 1
        while i < len(content_lines) and content_lines[i].strip() and not re.match(r"^(#{1,6})\s|^```|^~~~|^>|^\s*([-*+] |\d+[.] )", content_lines[i]):
            para.append(content_lines[i]); i += 1
        body.append("<p>%s</p>" % inline("\n".join(para), resolver, ids))
    if footnotes:
        body.append('<section class="footnotes" aria-labelledby="footnotes-title"><h2 id="footnotes-title">Notes</h2><ol>')
        for key, value in footnotes.items():
            body.append('<li id="fn-%s">%s <a href="#fnref-%s" aria-label="Back to reference">↩</a></li>' % (key, inline(value, resolver, ids), key))
        body.append("</ol></section>")
    return "\n".join(body), [{"id": k, "number": str(v)} for k, v in ids.items()]


def make_html(course: dict[str, Any], unit: dict[str, Any], article: str, index: int, total: int, headings: list[dict[str, str]]) -> str:
    def asset_version(name: str) -> str:
        asset = ROOT / "assets" / name
        return hashlib.sha256(asset.read_bytes()).hexdigest()[:12] if asset.is_file() else "dev"
    css_url = "../../assets/course.css?v=" + asset_version("course.css")
    js_url = "../../assets/course.js?v=" + asset_version("course.js")
    display = re.sub(r"^Semana\s+\d+\s*[—-]\s*", "", unit["title"], flags=re.I)
    title = html.escape(display)
    nav = "".join('<li><a href="#%s">%s</a></li>' % (h["id"], html.escape(h["title"])) for h in headings if h.get("level") == "2")
    prevnext = []
    def short(u): return re.sub(r"^Semana\s+\d+\s*[—-]\s*", "", u["title"], flags=re.I)
    if index: prevnext.append('<a rel="prev" href="%s">← %s</a>' % (html.escape(course["units"][index - 1]["output"]), html.escape(short(course["units"][index - 1]))))
    if index + 1 < total: prevnext.append('<a rel="next" href="%s">%s →</a>' % (html.escape(course["units"][index + 1]["output"]), html.escape(short(course["units"][index + 1]))))
    group = unit.get("group", "")
    eyebrow = ("Unidade %d de 15" % (index + 1)) if index < 15 else (("Leitura %d de %d" % (index + 1, total)) if group == "Leituras complementares" else "Orientação")
    return '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s · %s</title><link rel="stylesheet" href="%s"></head><body class="course-reader"><a class="skip-link" href="#reading-content">Pular para a leitura</a><a class="site-return" href="index.html">← %s · índice do curso</a><div class="reader-layout"><aside class="chapter-nav"><h2>%s</h2><a href="index.html">Índice do curso</a><nav aria-label="Nesta página"><ol>%s</ol></nav></aside><main class="reading-sheet" id="reading-content"><header class="chapter-header"><p class="eyebrow">%s</p><h1>%s</h1></header><details class="mobile-contents"><summary>Conteúdo</summary><ol>%s</ol></details><article class="prose">%s</article><p class="editorial-note"><a href="editorial.html">English editorial note and source provenance</a></p><nav class="chapter-pagination" aria-label="Navegação entre unidades">%s</nav></main></div><script src="%s" defer></script></body></html>''' % (title, html.escape(course["title"]), css_url, html.escape(course["title"]), html.escape(course["title"]), nav, eyebrow, title, nav, article, " · ".join(prevnext), js_url)


def build(config_path: Path, source_root_override: str | None = None, output_dir_override: str | None = None, report_path_override: str | None = None) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_root = Path(source_root_override or config.get("source_root", ".")).expanduser().resolve()
    output_dir = Path(output_dir_override or config.get("output_dir", f"courses/{config['slug']}"))
    if not output_dir.is_absolute(): output_dir = (Path.cwd() / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    units = config.get("units", [])
    if not units: raise ValueError("config.units must contain at least one chapter")
    entries = []
    by_source = {}
    for u in units:
        source = Path(u["source"])
        path = source if source.is_absolute() else source_root / source
        rel = path.resolve().relative_to(source_root)
        out = f"{slugify(u.get('id', u['title']))}.html"
        record = {"id": u.get("id", slugify(u["title"])), "title": re.sub(r"^Semana\s+\d+\s*[—-]\s*", "", u["title"], flags=re.I), "group": u.get("group", "main"), "source": rel.as_posix(), "output": out, "path": path}
        entries.append(record); by_source[rel.as_posix()] = record
    report = {"slug": config["slug"], "title": config.get("title", config["slug"]), "files": [], "transformations": [], "unresolved_links": [], "unresolved_markers": [], "diagram_markers": []}
    search_records: list[dict[str, Any]] = []
    # Build all source metadata first so links can resolve forward references.
    sources = {}
    for rec in entries:
        if not rec["path"].is_file(): raise FileNotFoundError(rec["path"])
        raw = rec["path"].read_text(encoding="utf-8")
        metadata, text, stripped = read_frontmatter(raw); sources[rec["source"]] = (raw, text, metadata, stripped)
    course = {"slug": config["slug"], "title": config.get("title", config["slug"]), "description": config.get("description", ""), "units": entries}
    for rec in entries:
        raw, text, metadata, stripped = sources[rec["source"]]
        for change in config.get("replacements", []):
            if change.get("source") != rec["source"]: continue
            found = text.count(change["find"])
            expected = int(change.get("count", found))
            if found != expected: raise ValueError(f"replacement count mismatch for {rec['source']}: expected {expected}, found {found}")
            text = text.replace(change["find"], change["replace"])
            report["transformations"].append({"file": rec["source"], "type": "declared-replacement", "count": found, "find": change["find"], "replace": change["replace"]})
        for addition in config.get("prepends", []):
            if addition.get("source") == rec["source"]:
                text = addition["text"] + "\n\n" + text
                report["transformations"].append({"file": rec["source"], "type": "declared-prepend", "action": "editorial-context"})
        if "[[" in text or "****" in text:
            report["unresolved_markers"].append({"file": rec["source"], "marker": "unconverted-wikilink-or-strong-artifact"})
            raise ValueError(f"unresolved publication marker in {rec['source']}")
        if stripped: report["transformations"].append({"file": rec["source"], "type": "frontmatter", "action": "removed-from-public"})
        report["files"].append({"source": rec["source"], "output": rec["output"], "sha256": hashlib.sha256(raw.encode()).hexdigest(), "bytes": len(raw.encode()), "word_count": len(re.findall(r"\b\w+\b", text, flags=re.UNICODE)), "frontmatter": metadata})
        def resolve(target: str) -> str:
            target = unquote(target)
            if target.startswith(("http://", "https://", "mailto:", "#")): return target
            if target.startswith("/"):
                report["unresolved_links"].append({"file": rec["source"], "target": target, "reason": "absolute-path"})
                return target
            path_part, sep, fragment = target.partition("#")
            candidate = (Path(rec["source"]).parent / path_part).as_posix() if path_part else rec["source"]
            candidate = PurePosixPath(candidate).as_posix()
            if candidate in by_source:
                return by_source[candidate]["output"] + (("#" + slugify(fragment)) if sep and fragment else "")
            if path_part.lower().endswith((".md", ".markdown")):
                report["unresolved_links"].append({"file": rec["source"], "target": target})
            return target
        def diagram(path: str) -> str:
            report["diagram_markers"].append({"file": rec["source"], "path": path})
            diagram_path = (source_root / path).resolve()
            try: diagram_path.relative_to(source_root.resolve())
            except ValueError: raise ValueError(f"diagram escapes source_root: {path}")
            if not diagram_path.is_file():
                report["unresolved_markers"].append({"file": rec["source"], "marker": "{{mermaid:%s}}" % path}); return ""
            diagram_text = diagram_path.read_text(encoding="utf-8")
            # Mermaid CLI produces the actual layout. Keep a readable edge list
            # beside it for screen readers and users who need a linear view.
            edges = []
            labels: dict[str, str] = {}
            for node, label in re.findall(r"([A-Za-z][\w-]*)\s*[\[\(]([^\]\)]+)[\]\)]", diagram_text):
                labels[node] = re.sub(r"^[\"']|[\"']$", "", label).replace("<br/>", " · ").replace("<br>", " · ").strip()
            edge_syntax = re.sub(r'([A-Za-z][\w-]*)\s*\["[^"\n]*"\]', r"\1", diagram_text)
            parsed_edges = re.findall(r"([A-Za-z][\w-]*)\s*(-->|-\.->|==>)\s*(?:\|([^|]+)\|\s*)?([A-Za-z][\w-]*)", edge_syntax)
            for left, arrow, edge_label, right in parsed_edges:
                edge = "%s %s %s%s" % (labels.get(left, left), "→" if "-." not in arrow else "⇢", labels.get(right, right), (" (%s)" % edge_label.strip()) if edge_label else "")
                if edge not in edges: edges.append(edge)
            if not edges: edges = ["Diagram source did not expose a labelled edge list."]
            edge_list = "".join("<li>%s</li>" % html.escape(x) for x in edges)
            diagram_dir = output_dir.parent.parent / "assets" / "course-diagrams"
            diagram_dir.mkdir(parents=True, exist_ok=True)
            diagram_theme = {"theme": "base", "themeVariables": {"fontFamily": "Georgia, serif", "fontSize": "17px", "primaryColor": "#e8dec0", "primaryTextColor": "#40372e", "lineColor": "#8a7458", "edgeLabelBackground": "#efe7d2"}, "flowchart": {"curve": "basis", "nodeSpacing": 28, "rankSpacing": 42}}
            diagram_css = ".node.question rect,.node.fact rect{fill:#e2dfc7!important;stroke:#8d805b!important}.node.exit rect,.node.norm rect{fill:#e9d6af!important;stroke:#9d7951!important}.node.success rect,.node.downstream rect{fill:#dbe0c9!important;stroke:#7d8c65!important}.node.review rect,.node.judgment rect{fill:#e1d4c6!important;stroke:#9b7965!important}.node rect{rx:0!important;ry:0!important;stroke-width:1px!important}.nodeLabel,.edgeLabel{font-family:Georgia,serif!important;color:#40372e!important}"
            palette = {"#eaf5fb":"#e2dfc7", "#1f6f9f":"#8d805b", "#fff5df":"#e9d6af", "#a35a00":"#9d7951", "#edf8f0":"#dbe0c9", "#2f7d4a":"#7d8c65", "#f5eff8":"#e1d4c6", "#7b3f8c":"#9b7965", "#26343a":"#40372e", "#365f73":"#8d805b"}
            styled_diagram = diagram_text
            for original_color, paper_color in palette.items(): styled_diagram = styled_diagram.replace(original_color, paper_color)
            render_key = styled_diagram + json.dumps(diagram_theme, sort_keys=True) + diagram_css
            asset_name = slugify(diagram_path.stem) + "-" + hashlib.sha256(render_key.encode()).hexdigest()[:12] + ".svg"
            asset_path = diagram_dir / asset_name
            if not asset_path.exists():
                compiler = shutil.which("mmdc")
                if not compiler: raise ValueError("Mermaid CLI (mmdc) is required to render diagrams")
                try:
                    with tempfile.TemporaryDirectory(prefix="study-lab-diagram-") as temp_dir:
                        theme_path = Path(temp_dir) / "theme.json"
                        css_path = Path(temp_dir) / "diagram.css"
                        styled_source = Path(temp_dir) / "diagram.mmd"
                        styled_source.write_text(styled_diagram, encoding="utf-8")
                        theme_path.write_text(json.dumps(diagram_theme), encoding="utf-8")
                        css_path.write_text(diagram_css, encoding="utf-8")
                        subprocess.run([compiler, "-i", str(styled_source), "-o", str(asset_path), "-c", str(theme_path), "-C", str(css_path), "-b", "#efe7d2", "-I", "diagram-" + asset_name[:-4], "-q"], check=True, capture_output=True, text=True)
                except (OSError, subprocess.CalledProcessError) as exc:
                    detail = getattr(exc, "stderr", "") or str(exc)
                    raise ValueError(f"Mermaid compilation failed for {path}: {detail[:500]}") from exc
            rel_asset = "../../assets/course-diagrams/" + asset_name
            return '<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="Diagrama, com rolagem horizontal em telas pequenas"><img src="%s" alt="Diagrama: %s"></div><figcaption>Deslize para percorrer o diagrama · <a href="%s" target="_blank" rel="noopener">Abrir em tamanho maior ↗</a></figcaption><details><summary>Relações em texto</summary><div class="diagram-text" role="group" aria-label="Representação textual do diagrama"><ul>%s</ul></div></details></figure>' % (html.escape(rel_asset, quote=True), html.escape("; ".join(edges)), html.escape(rel_asset, quote=True), edge_list)
        transformations: list[dict[str, Any]] = []
        source_lines = text.splitlines()
        for h_index, source_line in enumerate(source_lines):
            if re.match(r"^#\s+", source_line):
                removed = source_lines.pop(h_index)
                transformations.append({"file": rec["source"], "type": "heading", "action": "source-title-represented-in-page-header", "value": removed[2:].strip()})
                break
        article, _ = render_markdown("\n".join(source_lines), resolve, diagram, transformations)
        search_text = re.sub(r"```[\s\S]*?```", " ", text)
        search_text = re.sub(r"\{\{mermaid:[^}]+\}\}", " diagram ", search_text)
        search_text = re.sub(r"[#>*_`|]", " ", search_text)
        search_text = re.sub(r"\s+", " ", search_text).strip()
        search_records.append({"id": rec["id"], "title": rec["title"], "group": rec["group"], "href": rec["output"], "text": search_text})
        # derive heading labels from the rendered article for navigation
        headings = [{"level": level, "id": anchor, "title": html.unescape(re.sub("<[^>]+>", "", content))} for level, anchor, content in re.findall(r'<h([1-6]) id="([^"]+)"><a[^>]*>¶</a>(.*?)</h[1-6]>', article)]
        rec["path"].relative_to(source_root)  # validates source containment
        (output_dir / rec["output"]).write_text(make_html(course, rec, article, entries.index(rec), len(entries), headings), encoding="utf-8")
        report["transformations"].extend({"file": rec["source"], **x} for x in transformations)
    if report["unresolved_links"] or report["unresolved_markers"]:
        raise ValueError(json.dumps({"unresolved_links": report["unresolved_links"], "unresolved_markers": report["unresolved_markers"]}, indent=2))
    public = {"slug": course["slug"], "title": course["title"], "description": course["description"], "units": [{k: v for k, v in rec.items() if k in ("id", "title", "group", "source", "output")} | {"word_count": next(x["word_count"] for x in report["files"] if x["output"] == rec["output"])} for rec in entries]}
    (output_dir / "catalogue.json").write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "search-index.json").write_text(json.dumps(search_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance = {"course": course["slug"], "editorial": config.get("editorial", {}), "sources": [{"source": x["source"], "sha256": x["sha256"], "word_count": x["word_count"]} for x in report["files"]], "transformations": report["transformations"], "diagrams": [{"path": x["path"], "sha256": hashlib.sha256((source_root / x["path"]).read_bytes()).hexdigest()} for x in report["diagram_markers"]], "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output_dir / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    index_path = output_dir / "index.html"
    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        start, end = "<!-- COURSE_CONTENTS_START -->", "<!-- COURSE_CONTENTS_END -->"
        if start in index and end in index:
            groups: list[str] = []
            for group in dict.fromkeys(r["group"] for r in entries):
                members = [r for r in entries if r["group"] == group]
                lis = "".join('<li><a href="%s"><span class="unit-no">%02d</span><span class="unit-title">%s</span></a></li>' % (html.escape(r["output"]), entries.index(r) + 1, html.escape(r["title"])) for r in members)
                groups.append('<section class="course-group"><h3>%s</h3><ol>%s</ol></section>' % (html.escape(group), lis))
            replacement = start + "\n" + "\n".join(groups) + "\n" + end
            index = re.sub(re.escape(start) + r".*?" + re.escape(end), replacement, index, flags=re.S)
            index_path.write_text(index, encoding="utf-8")
    report_path = report_path_override or config.get("report_path")
    if report_path:
        rp = Path(report_path).expanduser(); rp.parent.mkdir(parents=True, exist_ok=True); rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="JSON build configuration")
    parser.add_argument("--source-root", help="Override source_root (useful for a portable config)")
    parser.add_argument("--output-dir", help="Override output_dir")
    parser.add_argument("--report-path", help="Override report_path")
    args = parser.parse_args()
    try:
        report = build(args.config.resolve(), args.source_root, args.output_dir, args.report_path)
    except Exception as exc:
        print(f"build failed: {exc}", file=sys.stderr); return 1
    print(json.dumps({"files": len(report["files"]), "transformations": len(report["transformations"]), "output": "ok"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
