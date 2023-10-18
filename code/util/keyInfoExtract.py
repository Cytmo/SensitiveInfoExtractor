from util.keySensitiveInfoUtil import *
from util.resultUtil import ResOut
from util.simpleUtil import *
import re

# 添加结果输出模块
res_out = ResOut()

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
    

def process_passwd_file(filename):
    passwd_file = open(filename)
    res = []
    for line in passwd_file.readlines():
        if line == "\n":
            continue
        line = line.rstrip("\n")
        data_tmp = line.split(":")
        if int(data_tmp[2]) < 1 or int(data_tmp[2]) > 999:
            res.append(SensitiveInformation(
                1, [1], data_tmp).change_to_json())
    res_out.add_new_json(filename, res)


def process_shadow_file(filename):
    shadow_file = open(filename)
    res = []
    for line in shadow_file.readlines():
        if line == "\n":
            continue
        line = line.rstrip("\n")
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

            # sensitiveInformation.print_sensitive()
            # res_out.add_new_json(filename,sensitiveInformation.change_to_json())
            res.append(sensitiveInformation.change_to_json())
    res_out.add_new_json(filename, res)


option_pattern = r'(?<=\")\s*,\s*(?=\")'

# 公钥认证文件匹配


def process_authorized_keys_file(filename):
    authorized_file = open(filename)
    res = []
    for line in authorized_file.readlines():
        if line == "\n":
            continue
        line = line.rstrip("\n")
        sensitiveInformation = SensitiveInformation(3)
        authorized_tmp = line.split(" ")
        clean_authorized_tmp = [s for s in authorized_tmp if s != ""]
        if clean_authorized_tmp[0] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [6], [clean_authorized_tmp[1], clean_authorized_tmp[2] if len(clean_authorized_tmp) >= 3 else ''])
        elif clean_authorized_tmp[1] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [6], [clean_authorized_tmp[2], clean_authorized_tmp[3] if len(clean_authorized_tmp) >= 4 else ''])
            options = re.split(option_pattern, clean_authorized_tmp[0])
            for items in options:
                if items[:5] == "comma":
                    sensitiveInformation.add_templete(
                        [7], [re.search(r'"(.*?)"', items).group(1)])
                elif items[:5] == "from=":
                    sensitiveInformation.add_templete(
                        [8], [re.search(r'"(.*?)"', items).group(1)])
        # sensitiveInformation.print_sensitive()
        # res_out.add_new_json(filename,sensitiveInformation.change_to_json())
        res.append(sensitiveInformation.change_to_json())
    res_out.add_new_json(filename, res)


# 公钥文件
def process_pub_file(filename, nameclean):
    pub_file = open(filename)
    res = []
    for line in pub_file.readlines():
        if line == "\n":
            continue
        line.rstrip("\n")
        sensitiveInformation = SensitiveInformation(4)
        pub_tmp = line.split(" ")
        clean_pub_tmp = [s for s in pub_tmp if s != ""]
        if clean_pub_tmp[0] == "ssh-rsa":
            sensitiveInformation.add_templete(
                [9], [clean_pub_tmp[1]])
        # sensitiveInformation.print_sensitive()
        # res_out.add_new_json(filename,sensitiveInformation.change_to_json())
        res.append(sensitiveInformation.change_to_json())
    res_out.add_new_json(filename, res)

# 私钥文件


def process_priv_file(filename):
    priv_file = open(filename)
    sensitiveInformation = SensitiveInformation(5)
    sensitiveInformation.add_templete(
        [10], [''.join(priv_file.readlines()[1:-1])])
    # sensitiveInformation.print_sensitive()
    res_out.add_new_json(filename, sensitiveInformation.change_to_json())