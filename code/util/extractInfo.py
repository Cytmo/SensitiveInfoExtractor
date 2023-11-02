from informationEngine.keyInfoExtract import *
from util.decompressionUtil import *
import shutil
from util.resultUtil import ResOut
from toStringUtils.universalUtil import *
from toStringUtils.configUtil import *
from toStringUtils.emlUtil import *
from toStringUtils.officeUtil import *
from toStringUtils.picUtil import *
from informationEngine.info_core import begin_info_extraction
from toStringUtils.officeUtil import *

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
        sensitive_info = begin_info_extraction(
            text, flag=1, file_path=file_path)
    else:
        sensitive_info = begin_info_extraction(text, file_path=file_path)
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

    pic_list = ocr_table_batch(file_path)

    [print(data) for data in pic_list[0][0:]]

    text_or_table_flag = is_png_text(pic_list[0])

    if text_or_table_flag:
        # is table
        pd_table_data = pd.DataFrame(pic_list[0][1:])
        print(pd_table_data)
        res = single_table_sensitive_extraction(pd_table_data)
    else:
        # is pic
        print(pic_list[0][1:])
        res = begin_info_extraction(pic_list[0], file_path=file_path)

    res_out.add_new_json(file_path, res)


# 判断图片识别结果（表格形式）还是文本
def is_png_text(info):
    if len(info[1]) > 1:
        logger.info(TAG + "is_png_text(): input is [table] png ")
        return True
    logger.info(TAG + "is_png_text(): input is [text] png ")
    return False

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

    if not file_path.endswith(".wps"):
        return
    time = datetime.now().strftime("%Y%m%d%H%M%S%f")
    os.makedirs("../workspace/wps/trans/wps/", exist_ok=True)
    copy_file_path = "../workspace/wps/trans/wps/copy_"+time+"_" + \
        os.path.basename(file_path)
    shutil.copy(file_path, copy_file_path)
    wps_file_name = copy_file_path.replace(".wps", ".doc")
    os.rename(copy_file_path, wps_file_name)
    text = docs_file(wps_file_name, type=".wps")
    os.rename(wps_file_name, copy_file_path)
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

    if not file_path.endswith(".dps"):
        return
    time = datetime.now().strftime("%Y%m%d%H%M%S%f")
    os.makedirs("../workspace/wps/trans/dps/", exist_ok=True)
    copy_file_path = "../workspace/wps/trans/dps/copy_"+time+"_" + \
        os.path.basename(file_path)
    shutil.copy(file_path, copy_file_path)
    wps_file_name = copy_file_path.replace(".dps", ".ppt")
    os.rename(copy_file_path, wps_file_name)
    text = ppts_file(wps_file_name, type=".dps")
    os.rename(wps_file_name, copy_file_path)
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
    if not file_path.endswith(".et"):
        return
    time = datetime.now().strftime("%Y%m%d%H%M%S%f")
    os.makedirs("../workspace/wps/trans/et/", exist_ok=True)
    copy_file_path = "../workspace/wps/trans/et/copy_"+time+"_" + \
        os.path.basename(file_path)
    shutil.copy(file_path, copy_file_path)
    et_doc_name = copy_file_path.replace(".et", ".xlsx")
    os.rename(copy_file_path, et_doc_name)
    text = xlsx_file(et_doc_name)
    os.rename(et_doc_name, copy_file_path)
    res_out.add_new_json(file_path, text)


######################### code config file ################################

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
def extract_code_file(file_path, nameclean):
    logger.info(TAG+"extract_code_file(): " + os.path.basename(file_path))
    extract_direct_read(file_path, os.path.basename(file_path))
    return


######################### e-mail file ########################################
extension_switch_eml = {
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


#  .eml文件读取和提取操作
def extract_eml(file_path, nameclean):
    logger.info(TAG+"extract_eml(): " + file_path.split("/")[-1])
    eml_header, eml_text, attach_files_list = eml_file(file_path)

    sensitive_info = []
    sensitive_info_text = []
    if "text" in eml_text:
        sensitive_info_text = begin_info_extraction(eml_text["text"])

    if not len(sensitive_info_text) == 0:
        logger.info(TAG+"extract_eml(): eml body has  sensitive infomation")
        sensitive_info.append(sensitive_info_text)

    if "table" in eml_text:
        logger.info(TAG+"extract_eml(): eml body has table")
        sensitive_info = sensitive_info+eml_text["table"]

    result = {}
    if eml_header != "":
        result["eml_header"] = eml_header
    if sensitive_info != []:
        result["sensitive_info"] = sensitive_info
    if attach_files_list != []:
        for item_path in attach_files_list:
            file_spilit = os.path.splitext(os.path.basename(item_path))
            for process_function, suffix_list in extension_switch_eml.items():
                if file_spilit[1] in suffix_list:
                    process_function(item_path, file_spilit[0])

        result["attach_files_list"] = attach_files_list

    if result != {}:
        res_out.add_new_json(file_path, result)
