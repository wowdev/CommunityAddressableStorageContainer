import http.server
import socketserver
import sys
import os
import threading
import hashlib

class request_handler(http.server.SimpleHTTPRequestHandler):
  def translate_path (self, path):
    pwd = os.getcwd()
    os.chdir("wwwroot")
    p = http.server.SimpleHTTPRequestHandler.translate_path (self, path)
    os.chdir (pwd)
    return p
  def send_head(self):
    path = self.translate_path(self.path)
    f = None
    if os.path.isdir(path):
      parts = urllib.parse.urlsplit(self.path)
      if not parts.path.endswith('/'):
        # redirect browser - doing basically what apache does
        self.send_response(http.HTTPStatus.MOVED_PERMANENTLY)
        new_parts = (parts[0], parts[1], parts[2] + '/',
                     parts[3], parts[4])
        new_url = urllib.parse.urlunsplit(new_parts)
        self.send_header("Location", new_url)
        self.end_headers()
        return None
      for index in "index.html", "index.htm":
        index = os.path.join(path, index)
        if os.path.exists(index):
          path = index
          break
      else:
        return self.list_directory(path)
    ctype = self.guess_type(path)
    try:
      f = open(path, 'rb')
    except OSError:
      self.send_error(http.HTTPStatus.NOT_FOUND, "File not found")
      return None
    try:
      self.send_response(http.HTTPStatus.OK)
      self.send_header("Content-type", ctype)
      fs = os.fstat(f.fileno())
      self.send_header("Content-Length", str(fs[6]))
      self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
      self.send_header("Etag", hashlib.md5(f.read()).hexdigest())
      f.seek(0, 0)
      self.end_headers()
      return f
    except:
      f.close()
      raise

configs = socketserver.TCPServer(("", 1119), request_handler)
cdn = socketserver.TCPServer(("", 80), request_handler)

threads = []
for server in [configs, cdn]:
  thread = threading.Thread (target = server.serve_forever)
  thread.start() 
 
for thread in threads: 
  thread.join()