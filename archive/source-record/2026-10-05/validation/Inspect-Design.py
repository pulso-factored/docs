"""Read-only inventory of downloaded artifact bundles; no execution of scripts."""
import base64
import gzip
import json
import re
from pathlib import Path

for path in sorted(Path('design').glob('*.html')):
    text = path.read_text(encoding='utf-8')
    scripts = dict(re.findall(r'<script[^>]*type="(__bundler/[^\"]+)"[^>]*>(.*?)</script>', text, re.S))
    manifest = json.loads(scripts['__bundler/manifest'])
    print('\nFILE', path.name)
    print('PAGE_ORDER', scripts.get('__bundler/page_order', 'none')[:2000])
    for key, entry in manifest.items():
        raw = base64.b64decode(entry['data'])
        if entry.get('compressed'):
            raw = gzip.decompress(raw)
        try:
            body = raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        if '__bundler/template' not in body:
            continue
        title = re.search(r'<title>(.*?)</title>', body, re.S)
        print('PAGE', key, title.group(1) if title else '(no title)', 'bytes', len(raw))
