#!/usr/bin/env python3
"""One loopback viewer; registered files remain the only document source."""
import argparse
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'state/live-viewer'
PORT = 59343
LIMIT = 5 * 1024 * 1024
LABEL = 'com.ethansk.codex-live-viewer'
spec = importlib.util.spec_from_file_location('snapshot_export', ROOT / 'scripts/create-viewer.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def revision(raw):
    return hashlib.sha256(raw).hexdigest()


def read_text(path):
    if path.stat().st_size > LIMIT:
        raise ValueError('This file is larger than 5 MB.')
    raw = path.read_bytes()
    if len(raw) > LIMIT or b'\0' in raw:
        raise ValueError('Only UTF-8 text files up to 5 MB are supported.')
    return raw, raw.decode('utf-8')


def atomic_json(path, data):
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump(data, out); out.flush(); os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


@contextmanager
def state_lock(state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Registration is CLI-only. No web endpoint can grant access to another path.
    with (state / 'registry.lock').open('a') as lock:
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def registry(state):
    path = state / 'files.json'
    return json.loads(path.read_text()) if path.exists() else {}


def register(source, state=STATE):
    source = Path(source).expanduser().resolve(strict=True)
    read_text(source)
    with state_lock(state):
        files = registry(state)
        by_path = {v['path']: k for k, v in files.items()}
        def add(path):
            key = by_path.get(str(path)) or secrets.token_urlsafe(32)
            by_path[str(path)] = key
            files.setdefault(key, {'path': str(path), 'links': {}})
            return key
        key = add(source)
        # Resolve only references present at explicit CLI registration. Later web
        # requests/source edits cannot expand this allowlist to arbitrary disk paths.
        links = {}
        for href in export.destinations(read_text(source)[1]):
            parsed = urlparse(href)
            if parsed.scheme not in ('', 'file') or parsed.netloc or href.startswith('#'):
                continue
            candidate = Path(unquote(parsed.path)).expanduser()
            if not candidate.is_absolute(): candidate = source.parent / candidate
            candidate = candidate.resolve()
            if candidate.is_file():
                links[href] = add(candidate)
        files[key]['links'] = links
        atomic_json(state / 'files.json', files)
    return key


class ViewerServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, state=STATE):
        self.state = Path(state)
        self.write_lock = threading.Lock()
        self.started_revision = revision(Path(__file__).read_bytes())
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Never log capability URLs or file contents.

    def send(self, code, value=b'', content_type='application/json', **headers):
        if not isinstance(value, bytes): value = json.dumps(value).encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(value)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for key, val in headers.items(): self.send_header(key, val)
        self.end_headers(); self.wfile.write(value)

    def context(self, write=False):
        expected = '127.0.0.1:' + str(self.server.server_port)
        if self.headers.get('Host') != expected:
            raise PermissionError('Invalid host.')
        if self.headers.get('Origin') not in (None, 'http://' + expected):
            raise PermissionError('Invalid origin.')
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        key = query.get('doc', [''])[0]
        if write and self.headers.get('X-Viewer-Document') != key:
            raise PermissionError('Invalid save request.')
        return parsed.path, query, key

    def document(self, key):
        doc = registry(self.server.state).get(key)
        if not doc: raise PermissionError('File access is not registered.')
        path = Path(doc['path'])
        # Registration pins the resolved path; do not follow a later symlink swap.
        if path.resolve() != path or not path.is_file():
            raise FileNotFoundError('Original file is no longer available.')
        return doc, path

    def do_GET(self):
        try:
            route, query, key = self.context()
            if route == '/health':
                return self.send(200, {'service': LABEL, 'root': str(ROOT), 'revision': self.server.started_revision})
            if route in ('/', '/index.html'):
                nonce = secrets.token_urlsafe(24)
                # One app shell, no document bytes or stale fallback embedded in it.
                page = (ROOT / 'assets/viewer.html').read_text().replace('__TITLE__', 'Live file viewer').replace('__NONCE__', nonce).replace('__DOCUMENT__', json.dumps({'source': '', 'live': True}))
                page = page.replace("connect-src 'none'", "connect-src 'self'").replace('img-src data:', "img-src data: 'self'")
                return self.send(200, page.encode(), 'text/html; charset=utf-8')
            doc, path = self.document(key)
            if route == '/api/document':
                raw, text = read_text(path)
                tag = revision(raw)
                if self.headers.get('If-None-Match') == '"' + tag + '"': return self.send(304)
                images, links = {}, {}
                for href, linked_key in doc['links'].items():
                    linked = registry(self.server.state).get(linked_key)
                    if not linked: continue
                    suffix = Path(linked['path']).suffix.lower()
                    if suffix in export.MIMES:
                        images[href] = '/api/resource?' + urlencode({'doc': linked_key})
                    else:
                        fragment = urlparse(href).fragment
                        links[href] = '/index.html?' + urlencode({'doc': linked_key}) + ('#' + fragment if fragment else '')
                return self.send(200, {'name': path.name, 'path': str(path), 'source': text, 'revision': tag, 'images': images, 'links': links, 'appearance': export.codex_appearance()})
            if route == '/api/resource' and path.suffix.lower() in export.MIMES:
                if path.stat().st_size > 20 * 1024 * 1024: raise ValueError('Image is too large.')
                return self.send(200, path.read_bytes(), export.MIMES[path.suffix.lower()])
            self.send(404, {'error': 'Not found.'})
        except PermissionError as error: self.send(403, {'error': str(error)})
        except (OSError, UnicodeError, ValueError) as error: self.send(400, {'error': str(error)})

    def do_POST(self):
        try:
            route, query, key = self.context(write=True)
            if route != '/api/document': return self.send(404, {'error': 'Not found.'})
            _, path = self.document(key)
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= LIMIT * 6 + 1024: raise ValueError('Invalid save size.')
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or not isinstance(payload.get('source'), str): raise ValueError('Invalid text file.')
            raw = payload['source'].encode('utf-8')
            if len(raw) > LIMIT or b'\0' in raw: raise ValueError('Invalid text file.')
            with self.server.write_lock:
                before = path.stat()
                if revision(read_text(path)[0]) != payload.get('revision'):
                    return self.send(409, {'error': 'This file changed somewhere else. Download your edits, then reload the file.'})
                fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
                try:
                    with os.fdopen(fd, 'wb') as out:
                        out.write(raw); out.flush(); os.fsync(out.fileno())
                    shutil.copystat(path, tmp)
                    # Check again immediately before replacement. This rejects
                    # external edits observed during the write; editors that ignore
                    # file locks still have the filesystem's small rename race.
                    current = path.stat()
                    if (before.st_ino, before.st_mtime_ns, before.st_size) != (current.st_ino, current.st_mtime_ns, current.st_size) or revision(read_text(path)[0]) != payload.get('revision'):
                        return self.send(409, {'error': 'This file changed somewhere else. Your edits have not been saved.'})
                    self.document(key)
                    os.replace(tmp, path)
                finally:
                    if os.path.exists(tmp): os.unlink(tmp)
            self.send(200, {'revision': revision(raw)})
        except PermissionError as error: self.send(403, {'error': str(error)})
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error: self.send(400, {'error': str(error)})


def health():
    try:
        with urlopen('http://127.0.0.1:%d/health' % PORT, timeout=1) as response:
            return json.load(response)
    except OSError: return None


def ensure_server():
    expected = revision(Path(__file__).read_bytes())
    running = health()
    if running:
        if running.get('service') != LABEL or running.get('root') != str(ROOT):
            raise RuntimeError('Viewer port is owned by another service.')
        if running.get('revision') == expected: return
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    interpreter = sys.executable
    # A user LaunchAgent has no interactive shell/pyenv setup. Prefer a stable
    # Homebrew entrypoint only when it is this exact tested interpreter.
    for candidate in ('/opt/homebrew/bin/python3', '/usr/local/bin/python3'):
        if Path(candidate).exists() and os.path.samefile(candidate, sys.executable):
            interpreter = candidate; break
    command = [interpreter, str(Path(__file__).resolve()), '--serve']
    if sys.platform == 'darwin':
        folder = Path.home() / 'Library/LaunchAgents'; folder.mkdir(exist_ok=True)
        plist = folder / (LABEL + '.plist')
        config = {'Label': LABEL, 'ProgramArguments': command, 'RunAtLoad': True, 'KeepAlive': True, 'ProcessType': 'Background', 'EnvironmentVariables': {'CODEX_HOME': str(STATE.parent.parent)}, 'StandardOutPath': '/dev/null', 'StandardErrorPath': '/dev/null'}
        plist.write_bytes(plistlib.dumps(config))
        domain = 'gui/' + str(os.getuid())
        probe = subprocess.run(['launchctl', 'print', domain + '/' + LABEL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode: subprocess.run(['launchctl', 'bootstrap', domain, str(plist)], check=True, stdout=subprocess.DEVNULL)
        else: subprocess.run(['launchctl', 'kickstart', '-k', domain + '/' + LABEL], check=True, stdout=subprocess.DEVNULL)
    else:
        if running: raise RuntimeError('Restart the existing viewer service after updating it.')
        subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(50):
        running = health()
        if running and running.get('service') == LABEL and running.get('revision') == expected: return
        time.sleep(.1)
    raise RuntimeError('Live viewer did not start.')


def open_viewer(source, line=None):
    source = Path(source).expanduser().resolve(strict=True)
    _, text = read_text(source)
    if line is not None and not 1 <= line <= len(text.splitlines()) + 1: raise ValueError('Line is outside this file.')
    key = register(source)
    ensure_server()
    return 'http://127.0.0.1:%d/index.html?' % PORT + urlencode({'doc': key}) + ('#L' + str(line) if line is not None else '')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?')
    parser.add_argument('--line', type=int)
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    if args.serve: ViewerServer(('127.0.0.1', PORT)).serve_forever()
    elif args.source: print(open_viewer(args.source, args.line))
    else: parser.error('Choose a source file.')
