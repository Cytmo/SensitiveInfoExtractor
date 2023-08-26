from fileUtil import File
from unrar import rarfile
import globalVar
import os


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
    print("Processing zip file:",filename)

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

    # 读取文件进行处理
    if process_function:
        process_function(root_directory +'/'+ File.get_parent_directory(file),file_spilit[0])
    else:
        print("Unsupported file format.",file.name)

