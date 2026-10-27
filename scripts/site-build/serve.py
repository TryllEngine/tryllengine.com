"""Local preview that resolves URLs like GitHub Pages does.

    py -3 scripts/site-build/serve.py [port]     ->  http://localhost:8000/

/features serves features.html, /blog/posts/<slug> serves its index.html,
and unknown paths get 404.html.
"""
import functools
import http.server
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        no_index = os.path.isdir(path) and not os.path.exists(os.path.join(path, 'index.html'))
        if (not os.path.exists(path) or no_index) and os.path.exists(path.rstrip('/\\') + '.html'):
            self.path = self.path.split('?', 1)[0].split('#', 1)[0] + '.html'
        elif not os.path.exists(path) and os.path.exists(os.path.join(ROOT, '404.html')):
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            return open(os.path.join(ROOT, '404.html'), 'rb')
        return super().send_head()

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Handler, directory=ROOT))
    print(f'Serving {ROOT} at http://localhost:{port}/')
    server.serve_forever()
