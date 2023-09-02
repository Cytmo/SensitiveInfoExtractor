from util.resultUtil import ResOut
from toStringUtils.universalUtil import *
from toStringUtils.configUtil import *
from toStringUtils.emlUtil import *
from toStringUtils.officeUtil import *
from toStringUtils.picUtil import *
from informationEngine.info_core import info_extraction

# 日志模块
from util.logUtils import LoggerSingleton
TAG = "util.extractInfo.py-"
logger = LoggerSingleton().get_logger()

# 结果模块
res_out = ResOut()
logger = LoggerSingleton().get_logger()


# 此处更换敏感信息提取api
def sensitive_info_detect(file_path, text):
    sensitive_info = info_extraction(text)
    res_out.add_new_json(file_path, sensitive_info)


# 各种文件的提取操作
def extract_universal(file_path, nameclean):
    logger.info(TAG+"extract_universal(): " + file_path.split("/")[-1])
    text = universal_textract(file_path)
    sensitive_info_detect(file_path, text)


def extract_ppt_dps(file_path, nameclean):
    logger.info(TAG+"extract_ppt(): " + file_path.split("/")[-1])
    # text = ppt_and_dps_file(file_path)
    # sensitive_info_detect(file_path, text)


def extract_xlsx(file_path, nameclean):
    logger.info(TAG+"extract_xlsx(): " + file_path.split("/")[-1])
    # text = universal_textract(file_path)
    text = xlsx_file(file_path)
    formatted_data = json.dumps(text, ensure_ascii=False)
    res_out.add_new_json(file_path, formatted_data)


def extract_wps(file_path, nameclean):
    logger.info(TAG+"extract_wps(): " + file_path.split("/")[-1])
    text = wps_file_text(file_path)
    sensitive_info_detect(file_path, text)


def extract_et(file_path, nameclean):
    logger.info(TAG+"extract_et(): " + file_path.split("/")[-1])
    text = et_file_text(file_path)
    # TODO extract_xlsx() 待处理
    sensitive_info_detect(file_path, text)


def extract_pic(file_path, nameclean):
    logger.info(TAG+"extract_pic(): " + file_path.split("/")[-1])
    text = ocr_table_batch(file_path)
    sensitive_info_detect(file_path, text[0])


def extract_eml(file_path, nameclean):
    logger.info(TAG+"extract_eml(): " + file_path.split("/")[-1])
    eml_header, eml_text = eml_file(file_path)
    eml_header = json.loads(eml_header)
    eml_text = json.loads(eml_text)
    sensitive_info = []
    sensitive_info_text = info_extraction(eml_text["text"])
    if not len(sensitive_info_text) == 0:
        logger.info(TAG+"extract_eml(): eml body has no sensitive infomation")
        sensitive_info.append(sensitive_info_text)

    if "table" in eml_text:
        logger.info(TAG+"extract_eml(): eml body has table")
        sensitive_info = sensitive_info+eml_text["table"]

    eml_header["body"] = sensitive_info

    res_out.add_new_json(file_path, eml_header)


def is_code_file(code_dir_or_file):
    target_substring = "python_fasts3-main"

    if not target_substring in code_dir_or_file:
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
            one_ak_sk = json.dumps(ak_sk)
            ak_sk = {}
            extract_out.append(one_ak_sk)

    # 特殊处理的项结果(ak与sk)+未特殊处理的原有项
    res = extract_out+result_stdout_copy
    res_out.add_new_json(code_dir_or_file, res)
    return True


def is_win_reg_file(file_path):

    if "system.hiv" in file_path or "sam/system" in file_path:
        logger.info(TAG+"is_win_reg_file(): " + file_path)
        reg_info = win_reg_file(
            file_path, file_path.replace("/system", "/sam"))
        data_list = [line for line in reg_info.split('\n') if line.strip()]
        cleaned_list = [line.replace('\x14', '') for line in data_list]
        file_path_tip = file_path+" "+"with " + \
            file_path.split("/")[-1].replace("system", "sam")
        res_out.add_new_json(file_path_tip, cleaned_list)
        return True

    if "sam.hiv" in file_path or "sam/sam" in file_path:
        return True
    return False


def is_bash_history(file_path):

    if "sh_history" in file_path:
        logger.info(TAG+"is_bash_history(): " + file_path)
        text = universal_file(file_path)
        sensitive_info_text = info_extraction(text)
        logger.info(sensitive_info_text)
        res_out.add_new_json(file_path, sensitive_info_text)
        return True

    return False


def is_token_file(file_path):

    if "token" in file_path:
        logger.info(TAG+"is_token_file(): " + file_path)
        text = universal_file(file_path)
        res_out.add_new_json(file_path, text)
        return True

    return False
