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

# TODO: .csv 调整
extension_switch_new = {
    # 解压
    process_rar_file: [".rar"],
    process_zip_file: [".zip"],

    # 各种格式文件提取
    extract_universal: [".txt", ".epub", ".bash_history"],
    extract_direct_read: [".md"],

    extract_pdf: [".pdf"],
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

    # 代码文件处理
    extract_code_file: [
        '.py', '.java', '.c', '.cpp', '.hpp', '.js', '.html', '.css', '.rb',
        '.php', '.swift', '.kt', '.go', '.rs', '.ts', '.pl', '.sh', '.sql',
        '.json', '.xml', '.m', '.r', '.dart', '.scala', '.vb', '.lua', '.coffee',
        '.ps1', 'Dockerfile', '.toml', '.h'
    ],

    # 带后缀的关键文件处理
    process_pub_file: [".pub"],
}


# 后缀匹配解析函数
extension_switch = {
    ".rar": process_rar_file,
    ".zip": process_zip_file,
    ".txt": extract_universal,
    ".md": extract_direct_read,
    ".doc": extract_doc,
    ".ppt": extract_ppt,
    ".dps": extract_dps,
    ".xlsx": extract_xlsx,
    ".wps": extract_wps,
    ".et": extract_et,
    ".eml": extract_eml,
    ".png": extract_pic,
    ".jpg": extract_pic,
    ".pub": process_pub_file,
    ".yml": extract_config,
    ".xml": extract_config,
    ".properties": extract_config,
    ".epub": extract_universal,
    ".csv": extract_universal,
    ".html": extract_universal,
    ".mp3": extract_universal,
    ".msg": extract_universal,
    ".odt": extract_universal,
    ".ogg": extract_universal,
    ".pdf": extract_universal,
    ".ps": extract_universal,
    ".rtf": extract_universal,
    ".tiff": extract_universal,
    ".wav": extract_universal,
}


# 按照文件类型分发各个文件
def spilit_process_file(file, root_directory):

    # 获取文件的后缀
    # 类方法：获取文件名后缀
    file_spilit = os.path.splitext(file.name)
    file_name = root_directory + '/' + File.get_parent_directory(file)

    # 后缀检测分发
    for process_function, suffix_list in extension_switch_new.items():
        if file_spilit[1] in suffix_list:
            process_function(file_name, file_spilit[0])
            return

    # 系统关键敏感信息提取开始
    # 判断文件是win reg 文件
    if is_win_reg_file(file_name):
        return

    # 判断是否是passwd文件
    if if_passwd_file(file_name, file_spilit[0]):
        process_passwd_file(file_name)
        return

    # 判断是否是shadow文件
    if if_shadow_file(file_name, file_spilit[0]):
        process_shadow_file(file_name)
        return

    # 判断是否是公钥文件
    if if_authorized_keys_file(file_name, file_spilit[0]):
        process_authorized_keys_file(file_name)
        return

    # 判断是否是私钥文件
    if if_private_keys_file(file_name, file_spilit[0]):
        process_priv_file(file_name)
        return

    # TODO: 下面更改放入通用提取接口

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
                logger.warning(TAG + "=>Unsupported file format: " + file_name)
    except Exception as e:
        logger.warning(TAG + "=>Unsupported file format: " + file_name)
        globalVar.set_error_list(file_name, e.stderr, "不支持该文件类型")
