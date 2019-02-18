import re
from collections import namedtuple

FORBIDDEN = 403
OK = 200
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
REQUEST_TIMEOUT = 408

DEFAULT_CONFIG = {'HOST': '',
                  'PORT': 8080,
                  'SOCKET_TIMEOUT': 15.0,
                  'ROOT_DIRECTORY': "./www",
                  'WORKERS': 10,
                  'MAX_BUFFSIZE': 1024,
                  'MAX_SOCKET_READ_ATTEMPTS': 5}


HTTPResponse = namedtuple('HTTPResponse', 'code mime_type length content')
FILE = namedtuple('FILE', 'ext content length')

NOT_ALLOWED_RESPONSE = HTTPResponse(code=METHOD_NOT_ALLOWED, mime_type=None, length=None, content=None)
TIMEOUT_RESPONSE = HTTPResponse(code=REQUEST_TIMEOUT, mime_type=None, length=None, content=None)

MIME_TYPES = {'html': 'text/html',
              'css': 'text/css',
              'txt': 'text/plain',
              'js': 'text/javascript',
              'jpg': 'image/jpeg',
              'jpeg': 'image/jpeg',
              'png': 'image/png',
              'gif': 'image/gif',
              'swf': 'application/x-shockwave-flash'}

ENDLINE = '\r\n'
# REQUEST_PATTERN = re.compile(r'(?P<method>[A-Z]*?)\s+(?P<resource>\S*?)(?P<params>\?\S*?)?\s+(?:HTTP\/\d\.\d)(?:{crlf}'
#                               '(?P<header>[\S\s]*?))?'
#                               '(?P<end_request>{crlf}{crlf})?'
#                               '(?P<data>.*)?'.format(crlf=ENDLINE), re.MULTILINE)
REQUEST_PATTERN = re.compile(r'(?P<method>[A-Z]*?)\s+(?P<resource>\S*?)(?P<params>\?\S*?)?\s+(?:HTTP\/\d\.\d{crlf})'
                             r'([\s\S]*)?'
                             r'(?P<end_request>{crlf}{crlf})?'
                             r'([\s\S]*)?'.format(crlf=ENDLINE), re.MULTILINE)

RESPONSE_GET_TEMPLATE = "{header}{crlf}" \
                        "Date: {date},{crlf}" \
                        "Server: Python Test{crlf}" \
                        "Accept-Ranges: bytes{crlf}" \
                        "Content-Length: {length}{crlf}" \
                        "Connection: close{crlf}" \
                        "Content-Type: {mime_type}{crlf}{crlf}" \
                        "{content}"

RESPONSE_HEAD_TEMPLATE = "{header}{crlf}" \
                         "Date: {date},{crlf}" \
                         "Server: Python Test{crlf}" \
                         "Content-Length: {length}{crlf}" \
                         "Connection: close{crlf}" \
                         "Content-Type: {mime_type}{crlf}{crlf}"

RESPONSE_SHORT_TEMPLATE = "{header}{crlf}" \
                          "Date: {date},{crlf}" \
                          "Server: Python Test{crlf}" \
                          "Connection: close{crlf}{crlf}"

RESPONSE_HEADERS = {OK: "HTTP/1.1 200 OK",
                    FORBIDDEN: "HTTP/1.1 403 Forbidden",
                    NOT_FOUND: "HTTP/1.1 404 Not Found",
                    METHOD_NOT_ALLOWED: "HTTP/1.1 405 Method Not Allowed",
                    REQUEST_TIMEOUT: 'HTTP/1.1 408 Request Timeout'}
