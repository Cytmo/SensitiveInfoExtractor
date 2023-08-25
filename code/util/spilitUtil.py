from fileUtil import File

# 各个文件的提取
def process_txt_file(filename):
    print("Processing text file:", filename)

def process_csv_file(filename):
    print("Processing CSV file:", filename)

def process_excel_file(filename):
    print("Processing Excel file:", filename)

def process_rar_file(filename):
    print("Processing rar file:",filename)

# 后缀匹配解析函数
extension_switch = {
    ".txt": process_txt_file,
    ".csv": process_csv_file,
    ".xlsx": process_excel_file,
    ".rar": process_rar_file
}

# 分发各个文件提取处理
def spilit_process_file(file,root_directory):
    # 获取文件的后缀
    file_extension = File.spilit_file_name(file)

    # 从字典中获取相应的处理函数，默认为 None
    process_function = extension_switch.get(file_extension, None)

    # 读取文件进行处理
    if process_function:
        process_function(root_directory + File.get_parent_directory(file))
    else:
        print("Unsupported file format.",file.name)

