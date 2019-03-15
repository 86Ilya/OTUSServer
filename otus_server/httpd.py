#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import socket
import logging
from optparse import OptionParser
from datetime import datetime
from Queue import Queue
from threading import Thread, current_thread

from methods import get, head, FileNotFound, MimeTypeNotRecognized
from constants import RESPONSE_HEADERS, RESPONSE_SHORT_TEMPLATE, RESPONSE_GET_TEMPLATE, RESPONSE_HEAD_TEMPLATE
from constants import METHOD_NOT_ALLOWED, NOT_ALLOWED_RESPONSE, DEFAULT_CONFIG, INTERNAL_CONFIG
from helpers import not_found_response, not_allowed_response, timeout_response

METHODS_ROUTER = {"GET": get, "HEAD": head}


class Worker(Thread):
    """
    Класс рабочего(воркера), основой класс программы, отвечает за обработку HTTP запросов.
    """

    def __init__(self, queue, config):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()
        self.buffsize = config["MAX_BUFFSIZE"]
        self.root_dir = config["ROOT_DIRECTORY"]
        self.end_line = config["ENDLINE"]
        self.req_pattern = re.compile(config["REQUEST_PATTERN"].format(crlf=self.end_line), re.MULTILINE)

    def read(self, connection):
        """
        Метод читает данные из соединения
        :param connection:
        :return re.Match object match, int size: Возвращаем объект re.Match, в котором возможно есть совпадения по
        регулярному выражению self.req_pattern.
        Так же возвращаем количество прочитанных байт.
        """
        size = 0
        recv_buff = bytearray(self.buffsize)
        recv_mview = memoryview(recv_buff)
        match = None

        while True:
            nbytes = connection.recv_into(recv_mview)
            if not nbytes:
                break
            size += nbytes
            recv_mview = recv_mview[nbytes:]
            match = self.req_pattern.match(recv_buff[:size])
            if match:
                break
        logging.debug(u"{}: recv_buff content is: {}".format(current_thread().name, recv_buff))
        return match, size

    def send_response(self, connection, match):
        """
        Метод обрабатывает полученный запрос: определяет метод для генерации ответа и посылает HTTPResponse
        :param connection:
        :param re.Match object match:
        :return:
        """
        if match:
            parsed_request = match.groupdict()
            logging.debug(u"{}: parsed request is: {}".format(current_thread().name, parsed_request))
            response = method_handler(parsed_request, self.root_dir)
            logging.debug("{}: response is: {}".format(current_thread().name, response))
            connection.sendall(response)
        else:
            connection.sendall(not_allowed_response())

    def get_connection(self):
        """
        Данный метод просто агрегирует несколько вызовов, чтобы не загромождать главный цикл
        :return:
        """
        logging.debug(u"{}: Waiting for connection from queue".format(current_thread().name))
        connection = self.queue.get()
        logging.debug(u"{}: Got connection".format(current_thread().name))
        return connection

    def run(self):
        while True:
            connection = self.get_connection()
            try:
                match, size = self.read(connection)
                self.send_response(connection, match)

            except FileNotFound as error:
                logging.debug(u"{}: {}".format(current_thread().name, error))
                connection.sendall(not_found_response())
            except MimeTypeNotRecognized as error:
                logging.debug(u"{}: {}".format(current_thread().name, error))
                connection.sendall(not_allowed_response())
            except socket.timeout as error:
                if size > 0 and not match:
                    connection.sendall(not_allowed_response())
                else:
                    logging.debug(u"{}: We have timeout error: {}".format(current_thread().name, error))
                    connection.sendall(timeout_response())
            except Exception as error:
                # Эта ошибка будет обработана в главном цикле
                raise
            finally:
                logging.debug(u"{}: Finished".format(current_thread().name))
                try:
                    logging.debug(u"{}: Closing connection...".format(current_thread().name))
                    connection.close()
                except Exception as error:
                    logging.debug(u"{}: Closing connection error: {}".format(current_thread().name, error))
                self.queue.task_done()


class ThreadPool(object):
    """
    Класс организующий распределение заданий между потоками
    """

    def __init__(self, num_threads, config):
        self.queue = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.queue, config)

    def add_task(self, task):
        self.queue.put(task)

    def wait_completion(self):
        self.queue.join()


def method_handler(parsed_request, root_dir):
    """
    Функция-роутер. Распредляет запросы по соответствующим обработчикам.
    :param dict parsed_request:
    :param basestring root_dir:
    :return string: Сформированный HTTP ответ
    """
    method = parsed_request.get("method", None)
    method = str(method)

    if method not in METHODS_ROUTER.keys():
        response = NOT_ALLOWED_RESPONSE
    else:
        response = METHODS_ROUTER[method](parsed_request, root_dir)
    header = RESPONSE_HEADERS.get(response.code, RESPONSE_HEADERS[METHOD_NOT_ALLOWED])
    if not response.content:
        template = RESPONSE_HEAD_TEMPLATE
    elif response.content and response.length:
        template = RESPONSE_GET_TEMPLATE
    else:
        template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, length=response.length, mime_type=response.mime_type,
                          content=response.content, crlf=config['ENDLINE'])
    return res


def main(config):
    """
    Главная функция программы. На вход принимает конфиг.
    Далее создаёт HTTP соединение, пул потоков и начинает принимать соединения.
    :param dict config:
    :return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config['HOST'], config['PORT']))
    sock.listen(config['WORKERS'])
    logging.info(
        u"Starting web server on '{}:{}' with {} workers and {} as root dir".format(config['HOST'], config['PORT'],
                                                                                    config['WORKERS'],
                                                                                    config['ROOT_DIRECTORY']))
    pool = ThreadPool(config['WORKERS'], config)

    try:
        while True:
            logging.debug(u"waiting for connection")
            connection, address = sock.accept()
            connection.settimeout(config['SOCKET_TIMEOUT'])
            logging.debug(u"We have connection from: {}".format(connection))
            pool.add_task(connection)
    except KeyboardInterrupt:
        logging.info(u"Keyboard interrupt. Stopping execution")
        pool.wait_completion()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=DEFAULT_CONFIG['PORT'])
    op.add_option("-w", "--workers", action="store", type=int, default=DEFAULT_CONFIG['WORKERS'])
    op.add_option("-r", "--rootdir", action="store", default=DEFAULT_CONFIG['ROOT_DIRECTORY'])
    (opts, args) = op.parse_args()
    config = DEFAULT_CONFIG.copy()
    config["PORT"] = opts.port
    config["WORKERS"] = opts.workers
    config["ROOT_DIRECTORY"] = opts.rootdir
    config.update(INTERNAL_CONFIG)
    logging.info(u"Starting server at port {} with workers {}".format(config["PORT"], config["WORKERS"]))
    try:
        main(config)
    except Exception as error:
        logging.exception(u"Unknown exception: {}".format(error))
