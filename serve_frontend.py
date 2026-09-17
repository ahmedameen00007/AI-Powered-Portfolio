"""
serve_frontend.py -- Threaded HTTP Server with Range request support for media files.
Prevents video streaming from blocking page navigation and fixes infinite reload issues.
"""

import os
import sys
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class ThreadedRangeHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler that supports:
    - Multi-threaded concurrent requests (ThreadingHTTPServer)
    - HTTP 206 Partial Content (Range headers) for video/audio streaming
    """

    def send_head(self):
        path = self.translate_path(self.path)

        if not os.path.exists(path) or os.path.isdir(path):
            return super().send_head()

        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        # Parse Range header: bytes=start-end
        match = re.match(r"bytes=(\d+)-(\d+)?", range_header)
        if not match:
            return super().send_head()

        try:
            file_size = os.path.getsize(path)
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1

            if start >= file_size:
                self.send_error(416, "Requested Range Not Satisfiable")
                return None

            end = min(end, file_size - 1)
            length = end - start + 1

            ctype = self.guess_type(path)
            f = open(path, "rb")
            f.seek(start)

            self.send_response(206)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(length))
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            return f
        except Exception:
            return super().send_head()


def run(port: int = 8080) -> None:
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, ThreadedRangeHTTPRequestHandler)
    print(f"Serving frontend on port {port} (threaded with Range support)...", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
