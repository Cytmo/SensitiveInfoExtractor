from unrar import rarfile
from util import globalVar
import zipfile
from util.logUtils import LoggerSingleton

# 解压模块


# 添加日志模块
logger = LoggerSingleton().get_logger()


# 处理rar解压
# 内存泄漏是否处理：是
def process_rar_file(filename, nameclean):
    rf = rarfile.RarFile(filename)
    rf.extractall('../workspace')
    globalVar.root_folder_list.put(
        '../workspace/'+nameclean)
    # logger.debug("Process compelete rar file:", filename)
    del rf
    del filename
    del nameclean


# 处理zip解压
# 内存泄漏是否处理：是
def process_zip_file(filename, nameclean):
    zip_file = zipfile.ZipFile(filename)
    zip_file.extractall('../workspace')
    globalVar.root_folder_list.put(
        '../workspace/'+nameclean)
    # logger.debug("Process compelete zip file:", filename)
    del zip_file
    del filename
    del nameclean
