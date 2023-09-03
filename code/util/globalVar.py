import yaml
import multiprocessing

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


def set_value(key, value):
    # 定义一个全局变量
    _global_dict[key] = value


def get_value(key):
    # 获得一个全局变量，不存在则提示读取对应变量失败
    try:
        return _global_dict[key]
    except:
        print('读取'+key+'失败\r\n')


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
