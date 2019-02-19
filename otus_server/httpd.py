#!/usr/bin/env python

import socket
import logging
from optparse import OptionParser
from datetime import datetime
from Queue import Queue
from threading import Thread, current_thread

from methods import get, head
from constants import RESPONSE_HEADERS, RESPONSE_SHORT_TEMPLATE, RESPONSE_GET_TEMPLATE, RESPONSE_HEAD_TEMPLATE, ENDLINE
from constants import REQUEST_PATTERN, METHOD_NOT_ALLOWED, NOT_ALLOWED_RESPONSE, REQUEST_TIMEOUT, DEFAULT_CONFIG

METHODS_ROUTER = {"GET": get, "HEAD": head}


def not_allowed_response():
    header = RESPONSE_HEADERS[METHOD_NOT_ALLOWED]
    template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, crlf=ENDLINE)
    return res


def timeout_response():
    header = RESPONSE_HEADERS[REQUEST_TIMEOUT]
    template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, crlf=ENDLINE)
    return res


class Worker(Thread):
    def __init__(self, queue, config):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()
        self.buffsize = config["MAX_BUFFSIZE"]
        self.root_dir = config["ROOT_DIRECTORY"]
        self.max_read_attempts = config["MAX_SOCKET_READ_ATTEMPTS"]

    def run(self):
        while True:
            logging.debug("{}: Waiting for connection from queue".format(current_thread().name))
            connection = self.queue.get()
            logging.debug("{}: Got connection".format(current_thread().name))
            size = 0
            recv_buff = bytearray(self.buffsize)
            recv_mview = memoryview(recv_buff)
            match = None
            attempts = self.max_read_attempts

            try:
                while attempts > 0:
                    nbytes = connection.recv_into(recv_mview)
                    if not nbytes:
                        break
                    size += nbytes
                    recv_mview = recv_mview[nbytes:]
                    match = REQUEST_PATTERN.match(recv_buff[:size])
                    if match:
                        break
                    attempts -= 1

                logging.debug("{}: recv_buff content is: {}".format(current_thread().name, recv_buff))
                if match:
                    parsed_request = match.groupdict()
                    logging.debug("{}: parsed request is: {}".format(current_thread().name, parsed_request))
                    response = method_handler(parsed_request, self.root_dir)
                    logging.debug("{}: response is: {}".format(current_thread().name, response))
                    connection.sendall(response)
                else:
                    connection.sendall(not_allowed_response())

            except socket.timeout as error:
                if size > 0 and not match:
                    connection.sendall(not_allowed_response())
                else:
                    logging.debug("{}: We have timeout error: {}".format(current_thread().name, error))
                    connection.sendall(timeout_response())
            except Exception as error:
                error_msg = "{}: We have unexpected error: recv_buf is: '{}', error is: '{}'".format(
                    current_thread().name, recv_buff, error)
                logging.debug(error_msg)
                raise
            finally:
                logging.debug("{}: Finished".format(current_thread().name))
                try:
                    logging.debug("{}: Closing connection...".format(current_thread().name))
                    connection.close()
                except Exception as error:
                    logging.debug("{}: Closing connection error: {}".format(current_thread().name, error))
                self.queue.task_done()


class ThreadPool(object):
    def __init__(self, num_threads, config):
        self.queue = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.queue, config)

    def add_task(self, task):
        self.queue.put(task)

    def wait_completion(self):
        self.queue.join()


def method_handler(parsed_request, root_dir):
    method = parsed_request.get("method", None)
    method = str(method)

    if method not in METHODS_ROUTER.keys():
        response = NOT_ALLOWED_RESPONSE
    else:
        response = METHODS_ROUTER[method](parsed_request, root_dir)
    header = RESPONSE_HEADERS.get(response.code, RESPONSE_HEADERS[METHOD_NOT_ALLOWED])
    if not response.content and response.length:
        template = RESPONSE_HEAD_TEMPLATE
    elif response.content and response.length:
        template = RESPONSE_GET_TEMPLATE
    else:
        template = RESPONSE_SHORT_TEMPLATE
    timestamp = datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = template.format(header=header, date=timestamp, length=response.length, mime_type=response.mime_type,
                          content=response.content, crlf=ENDLINE)
    return res


def main(config):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config['HOST'], config['PORT']))
    sock.listen(1)
    logging.info("")
    pool = ThreadPool(config['WORKERS'], config)

    try:
        while True:
            logging.debug("waiting for connection")
            connection, address = sock.accept()
            connection.settimeout(config['SOCKET_TIMEOUT'])
            logging.debug("We have connection from: {}".format(connection))
            pool.add_task(connection)
    except KeyboardInterrupt:
        logging.info("")
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
    logging.info("Starting server at port {} with workers {}".format(config["PORT"], config["WORKERS"]))
    try:
        main(config)
    except Exception as error:
        logging.exception("Unknown exception: {}".format(error))
