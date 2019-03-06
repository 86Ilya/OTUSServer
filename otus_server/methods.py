import os
import urllib
import logging
from constants import OK, FORBIDDEN, NOT_FOUND, MIME_TYPES, FILE, HTTPResponse, NOT_ALLOWED_RESPONSE
from threading import current_thread


def get_file(path):
    if os.path.exists(path):
        if '../' in path:
            return FORBIDDEN
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
            return get_file(path)
        ext = path.split(".")[-1]
        with open(path, 'r') as res:
            content = res.read()
            return FILE(ext=ext, content=content, length=len(content))
    else:
        return NOT_FOUND


def get(parsed_request, root_dir):

    resource = parsed_request.get("resource", None)
    if resource:
        resource = urllib.unquote(str(resource)).decode('utf8')
        path = os.path.join(root_dir, resource.lstrip('/'))
        logging.debug(u"{}: Trying to get file: {}".format(current_thread().name, path))
        local_file = get_file(path)
        if local_file in [FORBIDDEN, NOT_FOUND]:
            return HTTPResponse(code=local_file, mime_type=None, length=None, content=None)
        mime_type = MIME_TYPES.get(local_file.ext, None)
        if mime_type:
            return HTTPResponse(code=OK, mime_type=mime_type, length=local_file.length, content=local_file.content)
    return NOT_ALLOWED_RESPONSE


def head(parsed_request, root_dir):
    response = get(parsed_request, root_dir)
    if response.code == OK:
        return HTTPResponse(code=response.code, mime_type=response.mime_type, length=response.length, content=None)
    else:
        return response
