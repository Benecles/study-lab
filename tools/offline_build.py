#!/usr/bin/env python3
"""Modo ônibus build step. Run from the repo root after changing any page:

    python3 tools/offline_build.py

1. Adds <script src=".../assets/offline.js" defer> to every HTML page that lacks it.
2. Writes offline-manifest.json: every public file, plus directory URLs for index pages,
   and a content hash as the version (so saved copies refresh when the site changes).
"""
import hashlib, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP = ('.html', '.css', '.js', '.json', '.svg', '.ico', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.woff', '.woff2')
SKIP_DIRS = {'.git', 'tools', 'node_modules', '.claude'}
SKIP_FILES = {'offline-manifest.json', 'sw.js'}

def public_files():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith('.')]
        for f in files:
            if f.startswith('.') or f in SKIP_FILES or not f.lower().endswith(KEEP):
                continue
            out.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/'))
    return sorted(out)

def add_script(path):
    full = os.path.join(ROOT, path)
    s = open(full, encoding='utf-8').read()
    if 'assets/offline.js' in s or '</body>' not in s:
        return False
    depth = path.count('/')
    src = '../' * depth + 'assets/offline.js'
    s = s.replace('</body>', f'<script src="{src}" defer></script>\n</body>', 1)
    open(full, 'w', encoding='utf-8').write(s)
    return True

files = public_files()
added = [p for p in files if p.endswith('.html') and add_script(p)]
h = hashlib.sha1()
entries = []
for p in files:
    h.update(p.encode()); h.update(open(os.path.join(ROOT, p), 'rb').read())
    entries.append(p)
    if p == 'index.html' or p.endswith('/index.html'):
        entries.append(p[:-len('index.html')] or './')
man = {'version': h.hexdigest()[:12], 'files': entries}
json.dump(man, open(os.path.join(ROOT, 'offline-manifest.json'), 'w'), indent=0)
size = sum(os.path.getsize(os.path.join(ROOT, p)) for p in files)
print(f'offline: {len(files)} files, {size/1e6:.1f} MB, version {man["version"]}; script added to {len(added)} pages')
