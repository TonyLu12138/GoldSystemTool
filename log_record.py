#! /usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import datetime

# 获取当前脚本所在的目录
current_directory = os.path.dirname(__file__)
log_directory = os.path.join(current_directory, "logs")  # 日志文件夹路径

if not os.path.exists(log_directory):
    os.makedirs(log_directory)  # 如果文件夹不存在，创建它
    
class TaskLogger:
    def __init__(self, task_name):
        self.logger = logging.getLogger(task_name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 输出到控制台
        #console_handler = logging.StreamHandler(sys.stdout)
        #console_handler.setLevel(logging.DEBUG)
        #console_handler.setFormatter(formatter)
        #self.logger.addHandler(console_handler)

        # 输出到文件
        log_file = os.path.join(log_directory, f"log-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, level, message):
        level = level.upper()  # Convert level to uppercase
        if level == 'DEBUG':
            self.logger.debug(message)
        elif level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'CRITICAL':
            self.logger.critical(message)
        else:
            raise ValueError(f"Invalid log level: {level}")

class DebugLogger:
    def __init__(self, task_name, debug_enabled=False):
        self.logger = logging.getLogger(f"Debug_{task_name}")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        debug_log_file = os.path.join(log_directory, f"debug_log-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
        file_handler = RotatingFileHandler(debug_log_file, maxBytes=1000 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.debug_enabled = debug_enabled  # Set initial debug state

    #传入一个true的bool才能使用debug操作记录
    def set_debug(self, enabled=True):
        self.debug_enabled = enabled

    def log(self, message):
        if self.debug_enabled:
            self.logger.debug(message)