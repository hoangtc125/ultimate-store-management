import logging
import os, sys
import threading
import traceback
import yaml
from yaml.loader import SafeLoader
from collections import deque
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import TimedRotatingFileHandler

from app.core.project_config import settings
from app.core.helpper import mac_from_ip
from app.utils.time_utils import get_current_timestamp

class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename: str):
        self.__file_name = filename
        self.__base_dir = self.create_dir()
        TimedRotatingFileHandler.__init__(self, self.__base_dir + "/" + self.__file_name + "_logging.ini", when='midnight', interval=1)
  
    def doRollover(self):
        self.stream.close()
        self.__base_dir = self.create_dir()
        self.stream = open(self.__base_dir + "/" + self.__file_name + "_logging.ini", '+a', encoding="utf8")
        self.rolloverAt = self.rolloverAt + self.interval

    @staticmethod
    def create_dir(f_date_fmt = "YYYY/mm/dd"):
        base_dir = settings.LOG_DIR + "/log/" + str(datetime.now().date()).replace('-', '/')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return base_dir
    

class Logger:

    def __init__(self):
        self.__pool = {}
        self.__input_data_queue = deque()
        self.__is_locked = False
        self.__flag_event = threading.Event()
        self.__mapping = Logger.get_dir_mapping()
        self.__routers = list(self.__mapping.keys())

        loggers = {}
        for router in self.__routers:
            _logger = Logger.create_file_handler(src=router, dst=self.__mapping[router])
            loggers[router] = {
                "critical": _logger.critical,
                "warning": _logger.warning,
                "debug": _logger.debug,
                "error": _logger.error,
                "info": _logger.info,
            }
        self.__loggers = loggers

        logger_thread = threading.Thread(target=self.__log, args=())
        logger_thread.daemon = True
        logger_thread.start()

    @property
    def level(self):
        class Level:
            CRITICAL: str = "critical"
            WARNING: str = "warning"
            DEBUG: str = "debug"
            ERROR: str = "error"
            INFO: str = "info"
        return Level

    @property
    def tag(self):
        class Tag:
            START: str = "start"
            ADD: str = "add"
            END: str = "end"
        return Tag

    def __log(self):
        while True:
            try:
                if self.__pool:  # Logging timeout message
                    newest_id, newest_msg = list(self.__pool.items())[0]
                    if newest_msg['expired_at'] <= get_current_timestamp():
                        newest_msg['data'].append(("\n=================================================\n", logger.level.DEBUG))
                        for data in newest_msg['data']:
                            _message, _level = data
                            self.__loggers['timeout'][_level](_message)
                        self.__pool.pop(newest_id)

                res = self.__get_latest_data()  # mapping message into a group with similar request_id
                if not res:
                    continue

                request_id, latest_data ,tag, level = res

                if tag == self.tag.START:
                    self.__pool[request_id] = {}
                    self.__pool[request_id]['data'] = []
                    self.__pool[request_id]['expired_at'] = get_current_timestamp() + settings.LOG_TIME_OUT

                    request, request_user = latest_data
                    if request_user:
                        self.__pool[request_id]['data'].append((f"USER: {request_user.username}, ROLE: {request_user.role}", level))
                    if request:
                        self.__pool[request_id]['data'].append((f"CLIENT: client={request.client}, mac={mac_from_ip(request.client.host)}", level))
                        self.__pool[request_id]['data'].append((f"REQUEST: method={request.method}, url={request.url}", level))
                    continue

                if request_id not in self.__pool.keys():
                    self.__pool[request_id] = {}
                    self.__pool[request_id]['data'] = []
                    self.__pool[request_id]['expired_at'] = get_current_timestamp() + settings.LOG_TIME_OUT

                if tag == self.tag.ADD:
                    self.__pool[request_id]['data'].extend([(str(msg), level) for msg in latest_data])
                    continue

                path, response = latest_data
                if response:
                    self.__pool[request_id]['data'].append((f"RESPONSE: status={response.status_code}, process_time={response.headers['X-Process-Time']}", level))
                else:
                    self.__pool[request_id]['data'].append(("RESPONSE: None", level))
                self.__pool[request_id]['data'].append(("\n=================================================\n", level))

                router = path.split('/')[1]
                if router not in self.__routers:
                    router = 'stranger'
                
                for data in self.__pool[request_id]['data']:
                    _message, _level = data
                    self.__loggers[router][_level](_message)
                self.__pool.pop(request_id)
            except Exception as e:
                traceback.print_exc()
        
    def log(self, *args, tag='add', level='info'):
        request_id = Logger.get_http_request_id(sys._getframe(0))
        while not self.__is_locked:
            self.__is_locked = True
            self.__input_data_queue.append((request_id, args, tag, level))
            self.__is_locked = False
            self.__flag_event.set()
            return None

    def __get_latest_data(self):
        if not self.__input_data_queue:
            self.__flag_event.clear()
            self.__flag_event.wait()
        return self.__input_data_queue.popleft()

    @staticmethod
    def get_http_request_id(frame=sys._getframe(0), context = 1):
        while frame:
            if 'self' in frame.f_locals.keys() and isinstance(frame.f_locals['self'], BaseHTTPMiddleware):
                return id(frame.f_locals['scope'])
            frame = frame.f_back
        return 1

    @staticmethod
    def get_dir_mapping():
        with open(settings.LOG_DIR_MAPPING, encoding="utf8") as f:
            return yaml.load(f, Loader=SafeLoader)

    @staticmethod
    def create_file_handler(src, dst):
        logger = logging.getLogger(src)
        logger.setLevel(settings.LOG_LEVEL)
        f_format = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt="%H:%M:%S")
        f_handler = MyTimedRotatingFileHandler(filename=dst)
        f_handler.setFormatter(f_format)
        f_handler.suffix = "%Y-%m-%d"
        logger.addHandler(f_handler)
        return logger

logger = Logger()
