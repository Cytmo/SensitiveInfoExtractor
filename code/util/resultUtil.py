import json
import os


class ResOut:
    _instance = None
    res_json = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_new_json(self, file_path, sensitive_data):
        single_info = {"file_path": file_path,
                       "sensitive_data": sensitive_data}
        self.res_json.append(single_info)
        # TODO: 在main.py结束以后调用save_to_file()会导致只能写入main.py中调用add_new_json()的内容,无法写入在其他地方调用的add_new_json()
        self.save_to_file("output/output.json")

    def get_res_json(self):
        return self.res_json

    def clear_res_json(self):
        self.res_json = []

    def save_to_file(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'w') as file:
            json.dump(self.res_json, file, indent=4, ensure_ascii=False)
