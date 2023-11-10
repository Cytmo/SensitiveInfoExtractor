from util.logUtils import LoggerSingleton

# 系统关键敏感信息模块

# 添加日志模块
logger = LoggerSingleton().get_logger()

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
    "9": [21],  # 公钥
    "10": [22],  # 私钥
    "11": [21, 22]  # 公钥私钥对

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

    #控制台打印特殊敏感信息
    def print_sensitive(self):
        # # print("")
        # # print(sensitive_data_type.get(str(self.type)))
        templete_list = []
        for item in self.data_templete:
            templete_list = templete_list + \
                sensitive_data_templete.get(str(item))
        for i in range(len(templete_list)):
            if self.data[i] != "" and templete_list[i] != 0:
                logger.debug(sensitive_data_pairs.get(
                    str(templete_list[i]))+":" + self.data[i])

    #添加
    def add_templete(self, templete, data):
        self.data_templete = self.data_templete + templete
        self.data = self.data + data

    #特殊敏感信息封装成json
    def change_to_json(self):
        result = {"type": sensitive_data_type.get(str(self.type))}
        templete_list = []

        for item in self.data_templete:
            templete_list = templete_list + \
                sensitive_data_templete.get(str(item))

        for i in range(len(templete_list)):
            if self.data[i] != "" and templete_list[i] != 0:
                result[sensitive_data_pairs.get(
                    str(templete_list[i]))] = self.data[i]
        return result