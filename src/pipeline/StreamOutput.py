import cv2
import cv2.typing
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import numpy
from PIL import Image
import socketserver
import threading
import time

from config.ConnectionConfig import ConnectionConfig

class StreamOutput:
    _capture: cv2.typing.MatLike = numpy.array([])

    class StreamServer(socketserver.ThreadingMixIn, HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    def _make_handler(self_mjpeg): # type: ignore
        class StreamHandler(BaseHTTPRequestHandler):
            HTML = """
    <html>
        <head>
            <title>GRRTag</title>
            <style>
                body {
                    background-color: black;
                }

                img {
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                    max-width: 100%;
                    max-height: 100%;
                }
            </style>
        </head>
        <body>
            <img src="stream.mjpg" />
        </body>
    </html>
            """

            def do_GET(self):
                if self.path == "/":
                    content = self.HTML.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                elif self.path == "/stream.mjpg":
                    self.send_response(200)
                    self.send_header("Age", "0")
                    self.send_header("Cache-Control", "no-cache, private")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
                    self.end_headers()

                    try:
                        while True:
                            if not self_mjpeg._capture.any():
                                time.sleep(0.1)
                            else:
                                pil_im = Image.fromarray(self_mjpeg._capture) # type: ignore
                                stream = BytesIO()
                                pil_im.save(stream, format = "JPEG", quality = 10)
                                frame_data = stream.getvalue()

                                self.wfile.write(b"--FRAME\r\n")
                                self.send_header("Content-Type", "image/jpeg")
                                self.send_header("Content-Length", str(len(frame_data)))
                                self.end_headers()
                                self.wfile.write(frame_data)
                                self.wfile.write(b"\r\n")
                    except Exception as e:
                        print("Removed streaming client %s: %s", self.client_address, str(e))
                else:
                    self.send_error(404)
                    self.end_headers()

        return StreamHandler

    def _run(self, port: int) -> None:
        server = self.StreamServer(("", port), self._make_handler())
        server.serve_forever()

    def start_server(self, connection_config: ConnectionConfig) -> None:
        threading.Thread(target = self._run, daemon = True, args = (connection_config.video_port,)).start()

    def update(self, capture: cv2.typing.MatLike) -> None:
        self._capture = capture.copy()
