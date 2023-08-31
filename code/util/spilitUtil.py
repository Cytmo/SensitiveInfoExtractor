from util import globalVar
from util.fileUtil import File
from unrar import rarfile
import datetime
import queue
import zipfile
import os
# from util.extractInfo import *
from informationEngine.info_core import begin_info_extraction
# from toStringUtils.universalUtil import *
import re

# 添加结果输出模块
from util.resultUtil import ResOut
res_out = ResOut()


def convert_format_time(time_days):
    start_date = datetime.datetime(1970, 1, 1)
    target_date = start_date + datetime.timedelta(days=time_days)
    return target_date.strftime('%Y-%m-%d')


def process_rar_file(filename, nameclean):
    rf = rarfile.RarFile(filename)
    rf.extractall(globalVar.get_value("code_path")+'../workspace')
    globalVar.root_folder_list.put(
        globalVar.get_value("code_path")+'../workspace/'+nameclean)
    # print("Processing rar file:", filename)


def process_zip_file(filename, nameclean):
    # print("---------------"+filename+"  "+nameclean)
    # print(globalVar.get_value("code_path"))
    zip_file = zipfile.ZipFile(filename)
    zip_file.extractall(globalVar.get_value("code_path")+'../workspace')
    globalVar.root_folder_list.put(
        globalVar.get_value("code_path")+'../workspace/'+nameclean)
    # print("Processing zip file:", filename)


def if_passwd_file(filename, nameclean):
    if nameclean == "passwd":
        return True
    else:
        return False


def if_shadow_file(filename, nameclean):
    if nameclean == "shadow":
        return True
    else:
        return False


def if_authorized_keys_file(filename, nameclean):
    if nameclean == "authorized_keys":
        return True
    else:
        return False
    
def if_private_keys_file(filename, nameclean):
    with open(filename, 'r') as f:
        first_line = f.readline().strip()  # 读取第一行并去除首尾空白字符
    if first_line == "-----BEGIN OPENSSH PRIVATE KEY-----":
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
    "17": "用户状态",
    "18": "已授权公钥",
    "19": "该公钥所允许执行的命令",
    "20": "所允许使用该公钥的IP",
    "21": "公钥",
    "22": "私钥"

}

sensitive_data_type = {
    "0": "",
    "1": "Linux用户信息",
    "2": "Linux密码信息",
    "3": "公钥授权信息",
    "4": "公钥信息",
    "5": "私钥信息"
}

sensitive_data_templete = {
    "0": [],
    "1": [1, 0, 2, 3, 4, 5, 6],  # linux用户模板
    "2": [1, 17],  # linux密码伪用户
    "3": [1, 8, 9, 10],  # linux密码模板
    "4": [11, 13],  # linux密码无限期模板
    "5": [11, 12, 13, 14, 15, 16],  # linux密码有限期模板
    "6": [18, 4],  # 公钥及说明
    "7": [19],  # 公钥允许执行的命令
    "8": [20],  # 公钥所允许的IP
    "9": [21], #公钥
    "10": [22], #私钥
    "11": [21,22] #公钥私钥对

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
        if line == "\n":
            continue
        # sensitive_information_que.put(SensitiveInformation(1,1,line.split(":")))
        SensitiveInformation(1, [1], line.split(":")).print_sensitive()


def process_shadow_file(filename):
    shadow_file = open(filename)
    for line in shadow_file.readlines():
        if line == "\n":
            continue
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


option_pattern = r'(?<=\")\s*,\s*(?=\")'

# 公钥认证文件匹配
def process_authorized_keys_file(filename):
    authorized_file = open(filename)
    for line in authorized_file.readlines():
        if line == "\n":
            continue
        sensitiveInformation = SensitiveInformation(3)
        authorized_tmp = line.split(" ")
        clean_authorized_tmp = [s for s in authorized_tmp if s != ""]
        if clean_authorized_tmp[0] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [6], [clean_authorized_tmp[1],clean_authorized_tmp[2] if len(clean_authorized_tmp) >= 3 else ''])
        elif clean_authorized_tmp[1] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [6], [clean_authorized_tmp[2],clean_authorized_tmp[3] if len(clean_authorized_tmp) >= 4 else ''])
            options = re.split(option_pattern, clean_authorized_tmp[0])
            for items in options:
                if items[:5] == "comma":
                    sensitiveInformation.add_templete(
                        [7], [re.search(r'"(.*?)"', items).group(1)])
                elif items[:5] == "from=":
                    sensitiveInformation.add_templete(
                        [8], [re.search(r'"(.*?)"', items).group(1)])
        sensitiveInformation.print_sensitive()


# 公钥文件
def process_pub_file(filename,nameclean):
    pub_file = open(filename)
    for line in pub_file.readlines():
        if line == "\n":
            continue
        sensitiveInformation = SensitiveInformation(4)
        pub_tmp = line.split(" ")
        clean_pub_tmp = [s for s in pub_tmp if s != ""]
        if clean_pub_tmp[0] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [9],[clean_pub_tmp[1]])
        sensitiveInformation.print_sensitive()

# 私钥文件
def process_priv_file(filename):
    priv_file = open(filename)
    sensitiveInformation = SensitiveInformation(5)
    sensitiveInformation.add_templete(
        [10],[''.join(priv_file.readlines()[1:-1])])
    sensitiveInformation.print_sensitive()


# # 后缀匹配解析函数
# extension_switch = {
#     ".rar": process_rar_file,
#     ".zip": process_zip_file,
#     ".txt": extract_universal,
#     ".doc": extract_universal,
#     ".ppt": extract_ppt_dps,
#     ".dps": extract_ppt_dps,
#     ".xlsx": extract_xlsx,
#     ".wps": extract_wps,
#     ".et": extract_et,
#     ".eml": extract_eml,
#     ".png": extract_pic,
#     ".jpg": extract_pic,
#     ".pub": process_pub_file,
# }


# def spilit_process_file(file, root_directory):
#     # 获取文件的后缀
#     # 类方法：获取文件名后缀
#     file_spilit = os.path.splitext(file.name)

#     # 从字典中获取相应的处理函数，默认为 None
#     process_function = extension_switch.get(file_spilit[1], None)

#     file_name = root_directory + '/' + File.get_parent_directory(file)

#     # 读取文件进行处理
#     if process_function:
#         logger.info(TAG+"spilit_process_file(): " +
#                     file_name + ": " + file_spilit[0])
#         process_function(file_name, file_spilit[0])
#     else:
#         if if_passwd_file(file_name, file_spilit[0]):
#             process_passwd_file(file_name)
#         elif if_authorized_keys_file(file_name, file_spilit[0]):
#             process_authorized_keys_file(file_name)
#         elif if_private_keys_file(file_name, file_spilit[0]):
#             process_priv_file(file_name)
#         # print(file_name)
#         logger.info(TAG+"=>Unsupported file format: "+file_name)
