# -*- coding: utf-8 -*-
from constants import RESPONSE_HEADERS, RESPONSE_SHORT_TEMPLATE, METHOD_NOT_ALLOWED, REQUEST_TIMEOUT, NOT_FOUND
from constants import INTERNAL_CONFIG
from datetime import datetime


def not_found_response():
    """
    Функция формирующая HTTP ответ Not found
    :return string:
    """
    header = RESPONSE_HEADERS[NOT_FOUND]
    template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, crlf=INTERNAL_CONFIG["ENDLINE"])
    return res


def not_allowed_response():
    """
    Функция формирующая HTTP ответ Not allowed
    :return string:
    """
    header = RESPONSE_HEADERS[METHOD_NOT_ALLOWED]
    template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, crlf=INTERNAL_CONFIG["ENDLINE"])
    return res


def timeout_response():
    """
    Функция формирующая HTTP ответ Request Timeout'
    :return string:
    """
    header = RESPONSE_HEADERS[REQUEST_TIMEOUT]
    template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, crlf=INTERNAL_CONFIG["ENDLINE"])
    return res
