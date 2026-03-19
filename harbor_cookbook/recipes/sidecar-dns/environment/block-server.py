"""HTTP server that returns 403 for all requests."""

from http.server import HTTPServer, BaseHTTPRequestHandler


class BlockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(403)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ACCESS DENIED: This domain is blocked for this task.\n")

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_HEAD = do_GET

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 80), BlockHandler).serve_forever()
