import os
import logging
import colorlog
from datetime import datetime
from shutil import copyfile


"""
class LoggerSingleton: 日志打印单例模式，其作用是确保在整个程序中只有一个日志实例被创建和使用。
在项目python文件开头中加入以下代码即可访问
from util.log_utils import LoggerSingleton
TAG="**/**.py: "
logger = LoggerSingleton().get_logger()
logger.info(TAG+"***")
"""


class LoggerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance.init_logger()
        return cls._instance

    def init_logger(self):
        self.name = 'log'
        self.level = logging.DEBUG
        time = datetime.now().strftime("%Y%m%d%H%M%S%f")
        if not os.path.exists("log"):
            os.mkdir("log")
        # self.filename = 'log/' + time + 'info_extraction_.log'
        self.filename = 'log/' + "info_extraction" + '.log'
        logging.info("Logging to %s", self.filename)
        self.setup_logger()

    def setup_logger(self):
        # 设置logger
        logging.getLogger().handlers = []
        self.logger = logging.getLogger(name=self.name)
        self.logger.setLevel(level=self.level)

        self.logger.handlers = []
        # 初始化handler
        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(filename=self.filename)

        # 设置handler等级
        stream_handler.setLevel(level=logging.INFO)
        file_handler.setLevel(level=self.level)

        # 设置日志格式
        sf_format = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s-[line:%(lineno)d]-%(levelname)s-%(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            })

        stream_handler.setFormatter(sf_format)
        sf_format = logging.Formatter(
            "[line:%(lineno)d]-%(levelname)s-%(message)s")
        file_handler.setFormatter(sf_format)

        # 将handler添加到logger
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
