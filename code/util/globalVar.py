import yaml
import multiprocessing
from util.logUtils import LoggerSingleton

TAG = "utils.globalVar.py: "
logger = LoggerSingleton().get_logger()
"""
globalVar: 全局变量模块, 全局且多进程共享唯一
usage:
    from util import globalVar
"""


def _init():  # 初始化
    global _global_dict
    _global_dict = {}
    global root_folder_list
    root_folder_list = multiprocessing.Manager().Queue()
    global _sensitive_word
    _sensitive_word = multiprocessing.Manager().list()
    global _pic_hash
    _pic_hash = multiprocessing.Manager().dict()
    global error_list
    error_list = []
    error_list = multiprocessing.Manager().list()
    # 文件解析时的标志位, list[0]为是否处理非图片文件中的图片
    global flag_list
    flag_list = []
    flag_list = multiprocessing.Manager().list()
    # 是否输出无关联的敏感信息
    global unrelated_info_flag
    unrelated_info_flag = False
    # 是否启用认证信息搜索
    global auth_search_flag
    auth_search_flag = True


def set_error_list(file_path, value):
    # 定义一个全局变量
    error_list.append([file_path, value])


def get_error_list():
    # 获得一个全局变量，不存在则提示读取对应变量失败
    try:
        return error_list
    except:
        return []


def set_value(key, value):
    # 定义一个全局变量
    _global_dict[key] = value


def get_value(key):
    # 获得一个全局变量，不存在则提示读取对应变量失败
    try:
        return _global_dict[key]
    except:
        logger.debug('读取'+key+'失败\r\n')


def init_sensitive_word(yml_file_path):
    global _sensitive_word
    # 读取YAML文件
    with open(yml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    chinese_patterns = data.get('chinese_patterns', [])
    english_patterns = data.get('english_patterns', [])

    _sensitive_word = chinese_patterns+english_patterns


def get_sensitive_word():
    global _sensitive_word
    return _sensitive_word


def set_unrelated_info_flag(flag):
    global unrelated_info_flag
    unrelated_info_flag = flag


def get_unrelated_info_flag():
    global unrelated_info_flag
    return unrelated_info_flag


def set_auth_search_flag(flag):
    global auth_search_flag
    auth_search_flag = flag


def get_auth_search_flag():
    global auth_search_flag
    return auth_search_flag
