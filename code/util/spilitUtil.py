from fileUtil import File

#test

def process_txt_file(filename):
    print("Processing text file:", filename)

def process_csv_file(filename):
    print("Processing CSV file:", filename)

def process_excel_file(filename):
    print("Processing Excel file:", filename)

def process_rar_file(filename):
    print("Processing rar file:",filename)

extension_switch = {
    ".txt": process_txt_file,
    ".csv": process_csv_file,
    ".xlsx": process_excel_file,
    ".rar": process_rar_file
}

def spilit_process_file(file,root_directory):
    file_extension = File.spilit_file_name(file)

    # 从字典中获取相应的处理函数，默认为 None
    process_function = extension_switch.get(file_extension, None)

    if process_function:
        process_function(root_directory + File.get_parent_directory(file))
    else:
        print("Unsupported file format.",file.name)

