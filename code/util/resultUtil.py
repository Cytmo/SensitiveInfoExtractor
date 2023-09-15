import json
import os
from multiprocessing import Manager


"""
class ResOut: 结果输出模块, 全局且多进程共享唯一

usage:
    from util.resultUtil import ResOut
    res_out = ResOut()
"""


class ResOut:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.manager = Manager()
            cls._instance.res_json = cls._instance.manager.list()  # 使用 Manager 创建共享列表
        return cls._instance

    def add_new_json(self, file_path, sensitive_info):
        single_info = {"file_path": file_path,
                       "sensitive_info": sensitive_info}
        if len(sensitive_info) != 0:
            self.res_json.append(single_info)

    def get_res_json(self):
        return self.res_json

    def clear_res_json(self):
        self.res_json = []

    def save_to_file(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, 'w') as file:
            json.dump(list(self.res_json), file, indent=4, ensure_ascii=False)
