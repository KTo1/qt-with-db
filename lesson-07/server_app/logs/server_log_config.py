import os
import logging

from logging.handlers import TimedRotatingFileHandler

server_log = logging.getLogger('server.main')
formatter = logging.Formatter("<%(asctime)s> <%(levelname)s> <%(module)s> <%(message)s>")

file_name = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.join(file_name, 'server.log')

rotation_file_handler = TimedRotatingFileHandler(file_name, when='d', interval=1, backupCount=6, encoding='utf-8')
rotation_file_handler.setLevel(logging.DEBUG)
rotation_file_handler.setFormatter(formatter)

if not server_log.handlers:
    server_log.addHandler(rotation_file_handler)
server_log.setLevel(logging.DEBUG)