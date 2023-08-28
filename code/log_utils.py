import logging
import os
# import re
from shutil import copyfile
# import subprocess
# import argparse
# import sys
# import glob
# import time
import colorlog

current_work_dir = os.path.dirname(__file__)




class GetLog(object):
    def __init__(self):
        self.name = 'log'
        self.level = logging.DEBUG
        self.filename = 'test.log'
        logging.info("Logging to %s", self.filename)


    def get_log(self):

        #设置logger
        logging.getLogger().handlers = []
        logger = logging.getLogger(name=self.name)
        logger.setLevel(level=self.level)

        logger.handlers = []
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
        sf_format = logging.Formatter("[line:%(lineno)d]-%(levelname)s-%(message)s")
        file_handler.setFormatter(sf_format)
        
        # 将handler添加到self.__logger
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        #返回logger
        return logger
    
logger = GetLog().get_log()