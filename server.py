"""Free Openverse image retrieval. Python standard library only; no API key."""
import html
import json
import os
import random
import re
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
CACHE = {}
LOCK = Lock()
LAST_CALL = [0.0]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/images':
            if parsed.path not in ('/', '/index.html', '/style.css', '/script.js', '/favicon.ico'):
                return self.send_error(404)
            return super().do_GET()
        params = parse_qs(parsed.query)
        word = params.get('word', [''])[0].strip()
        seed = params.get('seed', [''])[0].strip()
        if not word or len(word) > 60 or len(seed) > 120:
            return self.reply(400, {'error': 'Invalid word or seed'})
        try:
            results = self.search(word.lower())
        except (HTTPError, URLError, TimeoutError, ValueError, OSError):
            results = []
        if not results:
            try:
                results = self.commons(word)
            except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                results = []
        if not results:
            with LOCK:
                results = list(CACHE.get(word.lower(), (0, []))[1])
                if not results:
                    results = [image for _, images in CACHE.values() for image in images]
        random.shuffle(results)
        return self.reply(200, {'query': word, 'results': results[:20]})

    def search(self, query):
        with LOCK:
            entry = CACHE.get(query)
            if entry and time.monotonic() - entry[0] < 1800:
                return list(entry[1])
        url = 'https://api.openverse.org/v1/images/?' + urlencode({'q': query, 'page_size': 20})
        req = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'DriftChanceLocalDemo/1.0 (educational artwork)'})
        for attempt in range(2):
            try:
                with urlopen(req, timeout=4) as response:
                    data = json.load(response)
                break
            except (HTTPError, URLError, TimeoutError, OSError):
                if attempt: raise
        results = []
        for item in data.get('results', []):
            thumb = item.get('thumbnail') or item.get('url')
            source = item.get('foreign_landing_url') or item.get('detail_url')
            if isinstance(thumb, str) and thumb.startswith('https://') and isinstance(source, str) and source.startswith('https://'):
                results.append({'thumb': thumb, 'source': source, 'title': str(item.get('title') or '')[:180], 'creator': str(item.get('creator') or '')[:120], 'license': str(item.get('license') or '').upper(), 'license_url': item.get('license_url') or ''})
        if results:
            with LOCK:
                CACHE[query] = (time.monotonic(), results)
        return results

    def commons(self, query):
        params = {'action': 'query', 'generator': 'search', 'gsrsearch': query,
                  'gsrnamespace': 6, 'gsrlimit': 20, 'prop': 'imageinfo',
                  'iiprop': 'url|extmetadata', 'iiurlwidth': 700, 'format': 'json'}
        req = Request('https://commons.wikimedia.org/w/api.php?' + urlencode(params),
                      headers={'User-Agent': 'DriftChanceLocalDemo/1.0 (educational artwork)', 'Accept': 'application/json'})
        with urlopen(req, timeout=5) as response:
            data = json.load(response)
        results = []
        for page in data.get('query', {}).get('pages', {}).values():
            info = (page.get('imageinfo') or [{}])[0]
            thumb, source = info.get('thumburl'), info.get('descriptionurl')
            if not thumb or not source:
                continue
            metadata = info.get('extmetadata', {})
            def plain(key):
                return html.unescape(re.sub(r'<[^>]+>', '', metadata.get(key, {}).get('value', ''))).strip()
            results.append({'thumb': thumb, 'source': source, 'title': page.get('title', ''),
                            'creator': plain('Artist'), 'license': plain('LicenseShortName')})
        if results:
            with LOCK:
                CACHE[query.lower()] = (time.monotonic(), results)
        return results

    def reply(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    host = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    print(f'Drift / Chance listening on {host}:{port}', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
