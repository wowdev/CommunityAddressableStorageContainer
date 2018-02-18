import http.server
import socketserver
import sys
import os
import threading
import hashlib
import urllib
import re

def copy_byte_range(infile, outfile, start=None, stop=None, bufsize=16*1024):
    '''Like shutil.copyfileobj, but only copy a range of the streams.
    Both start and stop are inclusive.
    '''
    if start is not None: infile.seek(start)
    while 1:
        to_read = min(bufsize, stop + 1 - infile.tell() if stop else bufsize)
        buf = infile.read(to_read)
        if not buf:
            break
        outfile.write(buf)

BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')
def parse_byte_range(byte_range):
    '''Returns the two numbers in 'bytes=123-456' or throws ValueError.
    The last number or both numbers may be None.
    '''
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last


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
      
    fs = os.fstat(f.fileno())
    file_len = fs[6]
        
    if 'Range' in self.headers:
      try:
          self.range = parse_byte_range(self.headers['Range'])
      except ValueError as e:
          self.send_error(400, 'Invalid byte range')
          return None
      first, last = self.range      
      
      if first >= file_len:
          self.send_error(416, 'Requested Range Not Satisfiable')
          return None
      
      if last is None or last >= file_len:
          last = file_len - 1
      response_length = last - first + 1
      
      self.send_response(206)
      self.send_header('Accept-Ranges', 'bytes')
      self.send_header('Content-Range',
                       'bytes %s-%s/%s' % (first, last, file_len))    
      self.send_header('Content-Length', str(response_length))
    else:
      self.send_response(http.HTTPStatus.OK)
      self.send_header("Content-Length", str(file_len))
      self.send_header("Etag", hashlib.md5(f.read()).hexdigest())
      self.range = None
      
    try:
      self.send_header("Content-type", ctype)
      self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
      f.seek(0, 0)
      self.end_headers()
      return f
    except:
      f.close()
      raise
      
  def copyfile(self, source, outputfile):
      if not self.range:
          return http.server.SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

      # SimpleHTTPRequestHandler uses shutil.copyfileobj, which doesn't let
      # you stop the copying before the end of the file.
      start, stop = self.range  # set in send_head()
      copy_byte_range(source, outputfile, start, stop)

configs = socketserver.TCPServer(("", 1119), request_handler)
cdn = socketserver.TCPServer(("", 80), request_handler)

threads = []
for server in [configs, cdn]:
  thread = threading.Thread (target = server.serve_forever)
  thread.start() 
 
for thread in threads: 
  thread.join()