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

# 后缀匹配解析函数
extension_switch = {
    ".rar": process_rar_file,
    ".zip": process_zip_file,
    ".txt": extract_universal,
    ".md": extract_direct_read,
    ".doc": extract_universal,
    ".ppt": extract_ppt_dps,
    ".dps": extract_ppt_dps,
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


#按照文件类型分发各个文件
def spilit_process_file(file, root_directory):

    # 获取文件的后缀
    # 类方法：获取文件名后缀
    file_spilit = os.path.splitext(file.name)

    # 从字典中获取相应的处理函数，默认为 None
    process_function = extension_switch.get(file_spilit[1], None)

    file_name = root_directory + '/' + File.get_parent_directory(file)

    # 读取文件进行处理
    if process_function:
        logger.info(TAG+"spilit_process_file(): " +
                    file_name + ": " + file_spilit[0])
        process_function(file_name, file_spilit[0])
    else:
        # 代码提取开始
        # 判断是代码目录或者代码文件
        if is_code_file(file_name):
            return
        
        # 系统关键敏感信息提取开始
        # 判断文件是win reg 文件
        if is_win_reg_file(file_name):
            process_win_reg_file(file_name)
            return
        # 判断文件是否是win reg绑定文件
        if rela_win_reg_file(file_name):
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
        # 判断是否是命令行历史记录
        if is_bash_history(file_name):
            return
        # 判断是否是token文件
        if is_token_file(file_name):
            return
        
        # TODO: 检查文件编码方式，如果能用文本打开读入就正常读入走文本接口
        logger.info(TAG+"=>Unsupported file format: "+file_name)
