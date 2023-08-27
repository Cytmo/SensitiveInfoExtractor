from fileUtil import File
from unrar import rarfile
import globalVar
import os
import zipfile
import queue


# 各个文件的提取
def process_txt_file(filename,nameclean):
    print("Processing text file:", filename)

def process_csv_file(filename,nameclean):
    print("Processing CSV file:", filename)

def process_excel_file(filename,nameclean):
    print("Processing Excel file:", filename)

def process_rar_file(filename,nameclean):
    rf = rarfile.RarFile(filename)
    rf.extractall(globalVar.get_value("code_path")+'/workspace')
    globalVar.root_folder_list.put(globalVar.get_value("code_path")+'/workspace/'+nameclean)
    print("Processing rar file:",filename)
    
def process_zip_file(filename,nameclean):
    zip_file = zipfile.ZipFile(filename)
    zip_file.extractall(globalVar.get_value("code_path")+'/workspace')
    globalVar.root_folder_list.put(globalVar.get_value("code_path")+'/workspace/'+nameclean)
    print("Processing zip file:",filename)

def if_passwd_file(filename,nameclean):
    if nameclean == "passwd":
        return True
    else:
        return False

sensitive_data_pairs = {
    "0":"",
    "1":"用户",
    "2":"UID(用户标识号)",
    "3":"GID(用户组别)",
    "4":"注释性描述",
    "5":"宿主目录",
    "6":"命令解释器"
}

sensitive_data_type = {
    "0":"",
    "1":"Linux用户信息",
    "2":"Linux密码信息",
}

sensitive_data_templete = {
    "0":[],
    "1":[1,0,2,3,4,5,6]
}

class SensitiveInformation:
    def __init__(self,type_in = 0,data_templete_in = 0,data_in=None):
        self.data = data_in
        self.data_templete = data_templete_in
        self.type = type_in
        return
    
    def print_sensitive(self):
        print("")
        print(sensitive_data_type.get(str(self.type)))
        templete_list = sensitive_data_templete.get(str(self.data_templete))
        for i in range(len(templete_list)):
            if self.data[i] is not "" and templete_list[i] is not 0:
                print(sensitive_data_pairs.get(str(templete_list[i]))+":" +self.data[i])
    

    
    
        

sensitive_information_que = queue.Queue()


def process_passwd_file(filename):
    passwd_file = open(filename)
    for line in passwd_file.readlines():
        # sensitive_information_que.put(SensitiveInformation(1,1,line.split(":")))
        SensitiveInformation(1,1,line.split(":")).print_sensitive()
    

process_passwd_file("/home/sakucy/networkCopitation/2023/data/linux/etc/passwd")


# 后缀匹配解析函数
extension_switch = {
    ".txt": process_txt_file,
    ".csv": process_csv_file,
    ".xlsx": process_excel_file,
    ".rar": process_rar_file,
    ".zip": process_zip_file
}

# 分发各个文件提取处理
def spilit_process_file(file,root_directory):
    # 获取文件的后缀
        # 类方法：获取文件名后缀
    file_spilit = os.path.splitext(file.name)

    # 从字典中获取相应的处理函数，默认为 None
    process_function = extension_switch.get(file_spilit[1], None)

    file_name = root_directory +'/'+ File.get_parent_directory(file)
    # 读取文件进行处理
    if process_function:
        process_function(file_name,file_spilit[0])
    else:
        if if_passwd_file(file_name,file_spilit[0]):
            process_passwd_file(file_name)
            
        print("Unsupported file format.",file.name)

