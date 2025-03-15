from util.resultUtil import ResOut
from util.fileUtil import File
from informationEngine.keyInfoExtract import *
import os
from util.extractInfo import *
from util.decompressionUtil import *
from toStringUtils.universalUtil import *
from util.logUtils import LoggerSingleton

# 添加日志模块
logger = LoggerSingleton().get_logger()

extension_switch_new = {
    # 解压
    process_rar_file: [".rar"],
    process_zip_file: [".zip"],

    # 各种格式文件提取
    extract_universal: [".txt", ".epub", ".bash_history"],
    extract_direct_read: [".md"],

    extract_pdf: [".pdf"],
    extract_csv: [".csv"],
    extract_doc: [".doc"],
    extract_wps: [".wps"],
    extract_docx: [".docx"],
    extract_ppt: [".ppt"],
    extract_dps: [".dps"],
    extract_pptx: [".pptx"],
    extract_xlsx: [".xlsx"],
    extract_et: [".et"],

    extract_eml: [".eml"],

    # 图片处理
    extract_pic: [".png", ".jpg"],

    # 配置文件处理
    extract_config: [".yml", ".xml", ".properties"],

    # 数据库文件处理
    extract_db:[".db"],

    # 代码文件处理
    extract_code_file: [
        '.py', '.java', '.c', '.cpp', '.hpp', '.js', '.html', '.css', '.rb',
        '.php', '.swift', '.kt', '.go', '.rs', '.ts', '.pl', '.sh', '.sql',
        '.json', '.xml', '.m', '.r', '.dart', '.scala', '.vb', '.lua', '.coffee',
        '.ps1', 'Dockerfile', '.toml', '.h', '.kt', '.js', '.wxss', '.wxml', '.html', '.php'
    ],


    # 带后缀的关键文件处理
    process_pub_file: [".pub"],

}


# 按照文件类型分发各个文件
def spilit_process_file(file, root_directory):
    """处理单个文件
    使用文件类型检测和处理函数映射进行处理
    """
    try:
        # 获取文件路径
        file_path = os.path.join(root_directory, File.get_parent_directory(file))
        # 获取文件名
        file_name = file.name
        TAG = "util.spilitUtil.py-"
        logger.info(TAG + "spilit_process_file(): " + file_name)
        
        # 使用新的统一文件处理函数
        process_file(file_path, file_name)
        
    except Exception as e:
        logger.error(TAG + "spilit_process_file(): " + str(e))

# 以下是旧的处理方式，保留注释以供参考
"""
def spilit_process_file(file, root_directory):

    # 获取文件的后缀
    # 类方法：获取文件名后缀
    filepathname = File.get_parent_directory(file)
    filepath = os.path.join(root_directory, filepathname)
    filename = file.name
    TAG = "util.spilitUtil.py-"
    logger.info(TAG+"spilit_process_file(): "+filename)
    file_extension = os.path.splitext(filename)[1]

    # 根据扩展名进入对应的处理函数
    for func, extensions in extension_switch_new.items():
        if file_extension in extensions:
            func(filepath, nameclean=filename)
            break
    else:
        # 默认处理（如果没有匹配到扩展名）
        isCode = is_token_file(filepath)
        if isCode:
            extract_code_file(filepath, nameclean=filename)
        else:
            extract_universal(filepath, nameclean=filename)
"""

# 系统关键敏感信息提取开始
# 判断文件是win reg 文件
if is_win_reg_file(file_name):
    return

# 判断是否是passwd文件
if if_passwd_file(file_name, file.name):
    process_passwd_file(file_name)
    return

# 判断是否是shadow文件
if if_shadow_file(file_name, file.name):
    process_shadow_file(file_name)
    return

# 判断是否是公钥文件
if if_authorized_keys_file(file_name, file.name):
    process_authorized_keys_file(file_name)
    return

# 判断是否是私钥文件
if if_private_keys_file(file_name, file.name):
    process_priv_file(file_name)
    return

# 判断是否是token文件
if is_token_file(file_name):
    return

try:
    with open(file_name, 'r') as file:
        first_line = file.readline()
        # 如果成功读取第一行数据，继续处理
        if first_line:
            extract_direct_read(file_name, os.path.splitext(file_name)[0])
        else:
            logger.debug(TAG + "=>Unsupported file format: " + file_name)
except Exception as e:
    logger.debug(TAG + "=>Unsupported file format: " + file_name)
    # globalVar.set_error_list(file_name, e, "不支持该文件类型")
