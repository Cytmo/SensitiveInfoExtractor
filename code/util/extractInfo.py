from util.resultUtil import ResOut
from toStringUtils.universalUtil import *
from toStringUtils.configUtil import *
from toStringUtils.emlUtil import *
from toStringUtils.officeUtil import *
from toStringUtils.picUtil import *
from informationEngine.info_core import begin_info_extraction

"""
extractInfo: 文件信息读取与敏感信息提取
"""


# 日志模块
from util.logUtils import LoggerSingleton
TAG = "util.extractInfo.py-"
logger = LoggerSingleton().get_logger()

# 结果模块
res_out = ResOut()
logger = LoggerSingleton().get_logger()


######################### 敏感信息提取api接口 ########################################


# 此处更换敏感信息提取api
def sensitive_info_detect(file_path, text, flag=0):
    if flag == 1:
        sensitive_info = begin_info_extraction(text, flag=1)
    else:
        sensitive_info = begin_info_extraction(text)
    res_out.add_new_json(file_path, sensitive_info)


######################### 常见文件 #################################################
# 常用文件提取操作, 如.txt...
def extract_universal(file_path, nameclean):
    logger.info(TAG+"extract_universal(): " + file_path.split("/")[-1])
    text = universal_textract(file_path)
    sensitive_info_detect(file_path, text)


# 直接读取文件文本
def extract_direct_read(file_path, namclean):
    logger.info(TAG+"extract_direct_read(): " + file_path.split("/")[-1])
    # 打开文件并读取其内容
    content = ""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    sensitive_info_detect(file_path, content)


# 配置文件读取和提取操作, 如.xml/.yml/.properties...
def extract_config(file_path, nameclean):
    logger.info(TAG+"extract_config(): " + file_path.split("/")[-1])
    text = universal_file(file_path)
    sensitive_info_detect(file_path, text, flag=1)


# 图片文件ocr读取和提取操作, 如.jpg/.png...
def extract_pic(file_path, nameclean):
    logger.info(TAG+"extract_pic(): " + file_path.split("/")[-1])
    text = ocr_table_batch(file_path)
    sensitive_info_detect(file_path, text[0])


######################### pdf file ###########################################


# .pdf文件读取和提取操作
def extract_pdf(file_path, nameclean):
    logger.info(TAG+"extract_pdf(): " + file_path.split("/")[-1])
    text = pdf_file(file_path)
    sensitive_info_detect(file_path, text)


######################### office/wps file########################################
# (1).doc/.wps/docx
# (2).ppt/.dps/.pptx
# (3).xlsx/.et


# (1-1).doc文件读取和提取操作
def extract_doc(file_path, nameclean):
    logger.info(TAG+"extract_doc(): " + file_path.split("/")[-1])
    text = docs_file(file_path, type=".doc")
    sensitive_info_detect(file_path, text)


# (1-2).wps文件读取和提取操作
def extract_wps(file_path, nameclean):
    logger.info(TAG+"extract_wps(): " + file_path.split("/")[-1])
    wps_file_name = file_path.replace(".wps", ".doc")
    os.rename(file_path, wps_file_name)
    text = docs_file(wps_file_name, type=".wps")
    os.rename(wps_file_name, file_path)
    sensitive_info_detect(file_path, text)


# (1-3).docx文件读取和提取操作
def extract_docx(file_path, nameclean):
    logger.info(TAG+"extract_docx(): " + file_path.split("/")[-1])
    text = docs_file(file_path, type=".docx")
    sensitive_info_detect(file_path, text)


# (2-1).ppt文件读取和提取操作
def extract_ppt(file_path, nameclean):
    logger.info(TAG+"extract_ppt(): " + file_path.split("/")[-1])
    text = ppts_file(file_path, type=".ppt")
    sensitive_info_detect(file_path, text)


# (2-2).dps文件读取和提取操作
def extract_dps(file_path, nameclean):
    logger.info(TAG+"extract_dps(): " + file_path.split("/")[-1])
    wps_file_name = file_path.replace(".dps", ".ppt")
    os.rename(file_path, wps_file_name)
    text = ppts_file(wps_file_name, type=".dps")
    os.rename(wps_file_name, file_path)
    sensitive_info_detect(file_path, text)


# (2-3).pptx文件读取和提取操作
def extract_pptx(file_path, nameclean):
    logger.info(TAG+"extract_pptx(): " + file_path.split("/")[-1])
    text = ppts_file(file_path, type=".pptx")
    sensitive_info_detect(file_path, text)


# (3-1).xlsx文件读取和提取操作
def extract_xlsx(file_path, nameclean):
    logger.info(TAG+"extract_xlsx(): " + file_path.split("/")[-1])
    text = xlsx_file(file_path)
    res_out.add_new_json(file_path, text)


# (3-2).et文件读取和提取操作
def extract_et(file_path, nameclean):
    logger.info(TAG+"extract_et(): " + file_path.split("/")[-1])
    et_doc_name = file_path.replace(".et", ".xlsx")
    os.rename(file_path, et_doc_name)
    text = xlsx_file(et_doc_name)
    os.rename(et_doc_name, file_path)
    res_out.add_new_json(file_path, text)


######################### e-mail file ########################################


# .eml文件读取和提取操作
def extract_eml(file_path, nameclean):
    logger.info(TAG+"extract_eml(): " + file_path.split("/")[-1])
    eml_header, eml_text, eml_attachment = eml_file(file_path)

    sensitive_info = []
    sensitive_info_text = begin_info_extraction(eml_text["text"])
    if not len(sensitive_info_text) == 0:
        logger.info(TAG+"extract_eml(): eml body has  sensitive infomation")
        sensitive_info.append(sensitive_info_text)

    if "table" in eml_text:
        logger.info(TAG+"extract_eml(): eml body has table")
        sensitive_info = sensitive_info+eml_text["table"]

    result = {
        "eml_header": eml_header,
        "sensitive_info": sensitive_info,
        "eml_attachment": eml_attachment
    }
    res_out.add_new_json(file_path, result)


######################### code config file ################################


# TODO 下面两个函数要消除
# .bash_history文件读取和提取操作
def is_bash_history(file_path):
    if "sh_history" in file_path:
        logger.info(TAG+"is_bash_history(): " + file_path)
        text = universal_file(file_path)
        sensitive_info_text = begin_info_extraction(text)
        logger.info(sensitive_info_text)
        res_out.add_new_json(file_path, sensitive_info_text)
        return True
    return False


# token文件读取和提取操作
def is_token_file(file_path):

    if "token" in file_path:
        logger.info(TAG+"is_token_file(): " + file_path)
        text = universal_file(file_path)
        res_out.add_new_json(file_path, text)
        return True

    return False


######################### code file########################################

# 源代码文件读取和提取操作
# TODO:需要重新整理CODE的识别
def extract_code_file(file_path, nameclean):
    # TODO: 添加处理
    return


def is_code_file(code_dir_or_file):
    # 代码后缀文件
    extension_code = [
        '.py', '.java', '.c', '.cpp', '.hpp', '.js', '.html', '.css', '.rb',
        '.php', '.swift', '.kt', '.go', '.rs', '.ts', '.pl', '.sh', '.sql',
        '.json', '.xml', '.m', '.r', '.dart', '.scala', '.vb', '.lua', '.coffee',
        '.ps1', 'Dockerfile', '.toml', '.h'
    ]

    code_config = ['Dockerfile', '.dockerignore', '.gitignore']

    flag_code_file = False

    if '.' in code_dir_or_file:
        file_extension = os.path.splitext(code_dir_or_file)[1]
        for item in extension_code:
            if file_extension == item:
                flag_code_file = True
                break

    for item in code_config:
        if str(code_dir_or_file).split("/")[-1] == item:
            flag_code_file = True
            break

    if not flag_code_file:
        return False

    result_stdout, result_stderr = source_code_file(code_dir_or_file)

    if len(result_stderr) == 0:
        logger.info(TAG+"is_code_file(): " + code_dir_or_file +
                    " , but none")
        return True

    logger.info(TAG+"is_code_file(): " + code_dir_or_file +
                " , has sensitive information.")

    result_stdout_json = json.loads(result_stdout)

    # 只保留 key和value
    result_stdout = [{"key": item["key"], "value": item["value"]}
                     for item in result_stdout_json]
    # 去重
    result_stdout_set = {tuple(item.items()) for item in result_stdout}
    result_stdout = [dict(item) for item in result_stdout_set]

    result_stdout_copy = result_stdout
    extract_out = []
    ak_sk = {}

    for item in result_stdout:
        if item["key"] == "ACCESSKEY":
            ak_sk["ACCESSKEY"] = item["value"]
            result_stdout_copy = [_item for _item in result_stdout_copy if not (
                _item["key"] == "ACCESSKEY" and _item["value"] == item["value"])]
            if not len(ak_sk) == 2:
                continue
        if item["key"] == "SECRETKEY":
            ak_sk["SECRETKEY"] = item["value"]
            result_stdout_copy = [_item for _item in result_stdout_copy if not (
                _item["key"] == "SECRETKEY" and _item["value"] == item["value"])]
            if not len(ak_sk) == 2:
                continue
        if len(ak_sk) == 2:
            extract_out.append(ak_sk)
            ak_sk = {}

    # 特殊处理的项结果(ak与sk)+未特殊处理的原有项
    res = extract_out+result_stdout_copy
    res_out.add_new_json(code_dir_or_file, res)
    return True
