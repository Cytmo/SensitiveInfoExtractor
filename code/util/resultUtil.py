import json
import os
from multiprocessing import Manager


class ResOut:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.manager = Manager()
            cls._instance.res_json = cls._instance.manager.list()  # 使用 Manager 创建共享列表
        return cls._instance

    def add_new_json(self, file_path, sensitive_data):
        single_info = {"file_path": file_path,
                       "sensitive_data": sensitive_data}
        self.res_json.append(single_info)

    def get_res_json(self):
        return self.res_json

    def clear_res_json(self):
        self.res_json = []

    def save_to_file(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Check if the file already exists and delete it if it does
        if os.path.exists(filename):
            os.remove(filename)

        with open(filename, 'w') as file:
            json.dump(list(self.res_json), file, indent=4, ensure_ascii=False)
