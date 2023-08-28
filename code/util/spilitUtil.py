from util import globalVar
from util.fileUtil import File
from unrar import rarfile
import datetime
import queue
import zipfile
import os


def convert_format_time(time_days):
    start_date = datetime.datetime(1970, 1, 1)
    target_date = start_date + datetime.timedelta(days=time_days)
    return target_date.strftime('%Y-%m-%d')


# 各个文件的提取
def process_txt_file(filename, nameclean):
    print("Processing text file:", filename)


def process_csv_file(filename, nameclean):
    print("Processing CSV file:", filename)


def process_excel_file(filename, nameclean):
    print("Processing Excel file:", filename)


def process_rar_file(filename, nameclean):
    rf = rarfile.RarFile(filename)
    rf.extractall(globalVar.get_value("code_path")+'/workspace')
    globalVar.root_folder_list.put(
        globalVar.get_value("code_path")+'/workspace/'+nameclean)
    print("Processing rar file:", filename)


def process_zip_file(filename, nameclean):
    zip_file = zipfile.ZipFile(filename)
    zip_file.extractall(globalVar.get_value("code_path")+'/workspace')
    globalVar.root_folder_list.put(
        globalVar.get_value("code_path")+'/workspace/'+nameclean)
    print("Processing zip file:", filename)


def if_passwd_file(filename, nameclean):
    if nameclean == "passwd":
        return True
    else:
        return False


sensitive_data_pairs = {
    "0": "",
    "1": "用户",
    "2": "UID(用户标识号)",
    "3": "GID(用户组别)",
    "4": "注释性描述",
    "5": "宿主目录",
    "6": "命令解释器",
    "7": "密码",
    "8": "加密方式",
    "9": "盐值",
    "10": "hash后密码",
    "11": "上次更改密码的日期",
    "12": "距下次允许更改天数",
    "13": "密码有效期",
    "14": "密码失效提前警告天数",
    "15": "密码过期后被禁用天数",
    "16": "用户的到期时间",
    "17": "用户状态"

}

sensitive_data_type = {
    "0": "",
    "1": "Linux用户信息",
    "2": "Linux密码信息",
}

sensitive_data_templete = {
    "0": [],
    "1": [1, 0, 2, 3, 4, 5, 6],  # linux用户模板
    "2": [1, 17],  # linux密码伪用户
    "3": [1, 8, 9, 10],  # linux密码模板
    "4": [11, 13],  # linux密码无限期模板
    "5": [11, 12, 13, 14, 15, 16]  # linux密码有限期模板
}

shadow_passwd_type = {
    "1": "MD5",
    "2a": "BlowFish",
    "2y": "BlowFish",
    "5": "SHA-256",
    "6": "SHA-512",
    "y": "非系统标准加密方式"
}


class SensitiveInformation:
    def __init__(self, type_in=0, data_templete_in=[0], data_in=[]):
        self.data = data_in
        self.data_templete = data_templete_in
        self.type = type_in
        return

    def print_sensitive(self):
        print("")
        print(sensitive_data_type.get(str(self.type)))
        templete_list = []
        for item in self.data_templete:
            templete_list = templete_list + \
                sensitive_data_templete.get(str(item))
        for i in range(len(templete_list)):
            if self.data[i] != "" and templete_list[i] != 0:
                print(sensitive_data_pairs.get(
                    str(templete_list[i]))+":" + self.data[i])

    def add_templete(self, templete, data):
        self.data_templete = self.data_templete + templete
        self.data = self.data + data


sensitive_information_que = queue.Queue()


def process_passwd_file(filename):
    passwd_file = open(filename)
    for line in passwd_file.readlines():
        # sensitive_information_que.put(SensitiveInformation(1,1,line.split(":")))
        SensitiveInformation(1, [1], line.split(":")).print_sensitive()


# process_passwd_file("/home/sakucy/networkCopitation/2023/data/linux/etc/passwd")

def process_shadow_file(filename):
    shadow_file = open(filename)
    for line in shadow_file.readlines():
        data_tmp = line.split(":")
        sensitiveInformation = SensitiveInformation(2)
        if data_tmp[1].count('$') < 4:
            sensitiveInformation.add_templete(
                [2], [data_tmp[0], "伪用户或者无密码,该用户不能登录"])
        else:
            split_passwd = data_tmp[1].split("$")
            sensitiveInformation.add_templete(
                [3], [data_tmp[0], shadow_passwd_type[split_passwd[1]], split_passwd[2], ''.join(split_passwd[3:])])

        if data_tmp[3] == "0" or data_tmp[3] == "":
            sensitiveInformation.add_templete(
                [4], [convert_format_time(int(data_tmp[2])), "无限"])
        else:
            sensitiveInformation.add_templete(
                [5], [convert_format_time(int(data_tmp[2]))]+data_tmp[3:7])

        sensitiveInformation.print_sensitive()


# process_shadow_file(
#     "../data/linux/etc/shadow")

# 后缀匹配解析函数
extension_switch = {
    ".txt": process_txt_file,
    ".csv": process_csv_file,
    ".xlsx": process_excel_file,
    ".rar": process_rar_file,
    ".zip": process_zip_file
}

# 分发各个文件提取处理


def spilit_process_file(file, root_directory):
    # 获取文件的后缀
    # 类方法：获取文件名后缀
    file_spilit = os.path.splitext(file.name)

    # 从字典中获取相应的处理函数，默认为 None
    process_function = extension_switch.get(file_spilit[1], None)

    file_name = root_directory + '/' + File.get_parent_directory(file)
    # 读取文件进行处理
    # if process_function:
    #     process_function(file_name, file_spilit[0])
    # else:
        # if if_passwd_file(file_name, file_spilit[0]):
        #     process_passwd_file(file_name)

        # print("Unsupported file format.", file.name)
