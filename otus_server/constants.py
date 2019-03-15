# -*- coding: utf-8 -*-
import re
import os
from collections import namedtuple

FORBIDDEN = 403
OK = 200
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
REQUEST_TIMEOUT = 408

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = {'HOST': '',
                  'PORT': 8080,
                  'ROOT_DIRECTORY': os.path.join(BASE_DIR, "www").decode('utf-8'),
                  'WORKERS': 10}

INTERNAL_CONFIG = {'MAX_BUFFSIZE': 1024,
                   'SOCKET_TIMEOUT': 15.0,
                   'ENDLINE': '\r\n',
                   'REQUEST_PATTERN': r'(?P<method>[A-Z]*?)\s+(?P<resource>\S*?)'
                                      r'(?P<params>\?\S*?)?\s+(?:HTTP\/\d\.\d{crlf})'
                                      r'([\s\S]*)?'
                                      r'(?P<end_request>{crlf}{crlf})?'
                                      r'([\s\S]*)?'}

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
