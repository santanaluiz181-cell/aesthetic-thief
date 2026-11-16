import functools
import http.server
import json
import os
import socketserver
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from blend_layers import blend_layers, render_markdown
from extract_aesthetic import extract_urls


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class TestAestheticThief(unittest.TestCase):
    def test_extract_urls_rejects_empty_list(self):
        with self.assertRaises(ValueError):
            extract_urls([], tempfile.mkdtemp())

    def test_blend_layers_rejects_unknown_source(self):
        with self.assertRaises(ValueError):
            blend_layers("nonexistent-style", "antigravity", "handmade-ink", "cli-pixel")

    def test_blend_layers_keeps_layers_isolated(self):
        spec = blend_layers("claude-editorial", "antigravity", "handmade-ink", "cli-pixel")
        self.assertEqual(spec["layers"]["surface"]["bg"], "#0B0D10")
        self.assertEqual(spec["layers"]["accent"]["color"], "#A64B3C")
        self.assertEqual(spec["layers"]["micro"]["radius"], "0px")
        self.assertEqual(spec["layers"]["structure"]["rhythm"], "editorial-generous")
        md = render_markdown(spec)
        self.assertIn("Antigravity Onyx", md)
        self.assertIn("CLI Pixel Terminal", md)

    def test_extract_and_blend_from_real_html_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = os.path.join(tmp, "site")
            out_dir = os.path.join(tmp, "captured")
            os.makedirs(site_dir, exist_ok=True)

            html = """<!DOCTYPE html>
            <html lang="en">
            <head>
              <title>Fixture Aesthetic</title>
              <style>
                :root { --demo-accent: rgb(166, 75, 60); }
                body { background: rgb(11, 13, 16); color: rgb(242, 244, 248); font-family: monospace; }
                button { border-radius: 6px; padding: 10px 16px; }
              </style>
            </head>
            <body>
              <h1>Hello Craft</h1>
              <button>Run</button>
            </body>
            </html>"""
            with open(os.path.join(site_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html)

            handler = functools.partial(QuietHandler, directory=site_dir)
            httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()

            try:
                results = extract_urls([f"http://127.0.0.1:{port}/index.html"], out_dir)
            finally:
                httpd.shutdown()

            self.assertEqual(len(results), 1)
            item = results[0]
            self.assertTrue(os.path.isfile(item["screenshots"]["desktop"]))
            self.assertTrue(os.path.isfile(item["screenshots"]["mobile"]))
            self.assertIn("--demo-accent", item["cssVars"])

            tokens_path = os.path.join(out_dir, item["slug"], "tokens.json")
            self.assertTrue(os.path.isfile(tokens_path))

            blended = blend_layers("claude-editorial", tokens_path, "handmade-ink", "cli-pixel")
            self.assertEqual(blended["layers"]["surface"]["bg"], "rgb(11, 13, 16)")
            self.assertEqual(blended["layers"]["micro"]["radius"], "0px")


if __name__ == "__main__":
    unittest.main()
