from util.resultUtil import ResOut
from toStringUtils.universalUtil import *
from toStringUtils.configUtil import *
from toStringUtils.emlUtil import *
from toStringUtils.officeUtil import *
from toStringUtils.picUtil import *
from informationEngine.info_core import begin_info_extraction

# 日志模块
from util.logUtils import LoggerSingleton
TAG = "util.extractInfo.py-"
logger = LoggerSingleton().get_logger()

# 结果模块
res_out = ResOut()
logger = LoggerSingleton().get_logger()


# 此处更换敏感信息提取api
def sensitive_info_detect(file_path, text):
    sensitive_info = begin_info_extraction(text)
    res_out.add_new_json(file_path, sensitive_info)


# 各种文件的提取操作
def extract_universal(file_path, nameclean):
    logger.info(TAG+"extract_universal(): " + file_path.split("/")[-1])
    text = universal_textract(file_path)
    sensitive_info_detect(file_path, text)


def extract_ppt_dps(file_path, nameclean):
    logger.info(TAG+"extract_ppt(): " + file_path.split("/")[-1])
    text = ppt_and_dps_file(file_path)
    sensitive_info_detect(file_path, text)


def extract_xlsx(file_path, nameclean):
    logger.info(TAG+"extract_xlsx(): " + file_path.split("/")[-1])
    # TODO extract_xlsx() 待处理
    text = universal_textract(file_path)
    sensitive_info_detect(file_path, text)


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
    # text = ocr_textract(file_path)
    text = ocr_paddleocr(file_path)
    text_string = "\n".join(text)
    logger.info(TAG+"extract_pic(): picture information")
    logger.info(TAG+"extract_pic(): " + text_string)
    sensitive_info_detect(file_path, text_string)


def extract_eml(file_path, nameclean):
    logger.info(TAG+"extract_eml(): " + file_path.split("/")[-1])
    text = eml_file(file_path)
    sensitive_info_detect(file_path, text)
