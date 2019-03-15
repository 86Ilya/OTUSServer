# -*- coding: utf-8 -*-
import os
import urllib
import logging
from constants import OK, FORBIDDEN, MIME_TYPES, FILE, HTTPResponse
from threading import current_thread


class FileNotFound(ValueError):
    pass


class MimeTypeNotRecognized(ValueError):
    pass


def get_final_path(rood_dir, path):
    """
    Нормализуем путь и конкатенируем его с нашим корневым каталогом
    :param str rood_dir:
    :param str path:
    :return str:
    """
    n_path = os.path.normpath(path).lstrip('/')
    final_path = os.path.join(rood_dir, n_path)
    if os.path.exists(final_path):
        if os.path.isdir(final_path):
            final_path = os.path.join(final_path, 'index.html')
            if not os.path.exists(final_path):
                return None
        return final_path


def get_file(root_dir, path):
    """
    Возвращаем файл по указанному пути, относительно корневого каталога.
    Если файл не найден, то возвращаем None
    :param str root_dir:
    :param str path:
    :return FILE:
    """
    final_path = get_final_path(root_dir, path)
    if final_path:
        ext = final_path.split(".")[-1]
        with open(final_path, 'r') as res:
            content = res.read()
            return FILE(ext=ext, content=content, length=len(content))


def get_file_info(root_dir, path):
    """
    Если по данному пути находится файл то возвращаем его размер, Иначе None
    :param str root_dir:
    :param str path:
    :return FILE: Именованный кортеж с content = None
    """
    final_path = get_final_path(root_dir, path)
    if final_path:
        ext = final_path.split(".")[-1]
        length = os.path.getsize(final_path)
        return FILE(ext=ext, content=None, length=length)


def get(parsed_request, root_dir):
    """
    Обрабатываем полученный запрос и возвращаем HTTP ответ с запрошенным файлом, если файл не найден, то
    вызываем ошибку.
    :param parsed_request:
    :param str root_dir:
    :return HTTPResponse:
    """
    resource = parsed_request.get("resource", None)
    if not resource:
        # Если пытаемся что-то запросить и не указываем что, то:
        return HTTPResponse(code=FORBIDDEN, mime_type=None, length=None, content=None)

    resource = urllib.unquote(str(resource)).decode('utf8')
    logging.debug(u"{}: Trying to get file: {}".format(current_thread().name, resource))
    local_file = get_file(root_dir, resource)
    if local_file is None:
        raise FileNotFound(u"File {} not found".format(resource))
    mime_type = MIME_TYPES.get(local_file.ext, None)
    if mime_type is None:
        raise MimeTypeNotRecognized(u"Unknown Mime type: {}".format(mime_type))
    return HTTPResponse(code=OK, mime_type=mime_type, length=local_file.length, content=local_file.content)


def head(parsed_request, root_dir):
    """
    Обрабатываем полученный запрос и возвращаем HTTP ответ с информацией о запрошенном файле, если файл не найден, то
    вызываем ошибку.
    :param parsed_request:
    :param str root_dir:
    :return HTTPResponse:
    """
    resource = parsed_request.get("resource", None)
    if not resource:
        # Если пытаемся что-то запросить и не указываем что, то:
        return HTTPResponse(code=FORBIDDEN, mime_type=None, length=None, content=None)
    resource = urllib.unquote(str(resource)).decode('utf8')
    logging.debug(u"{}: Trying to get info about file: {}".format(current_thread().name, resource))
    local_file = get_file_info(root_dir, resource)
    if local_file is None:
        raise FileNotFound(u"File {} not found".format(resource))
    mime_type = MIME_TYPES.get(local_file.ext, None)
    if mime_type is None:
        raise MimeTypeNotRecognized(u"Unknown Mime type: {}".format(mime_type))

    return HTTPResponse(code=OK, mime_type=mime_type, length=local_file.length, content=local_file.content)
