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
from toStringUtils.databaseUtil import *

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
    # 分割文本，每2000行为一个部分
    lines = text.split('\n')
    chunks = [lines[i:i + 2000] for i in range(0, len(lines), 2000)]

    # if len(chunks) > 1:
    #     print(len(chunks))

    # 用于存储所有块中发现的敏感信息
    all_sensitive_info = []

    # 遍历每个文本块
    for chunk in chunks:
        chunk_text = '\n'.join(chunk)
        try:
            # 根据flag标志调用不同的处理方式
            if flag == 1:
                sensitive_info = begin_info_extraction(
                    chunk_text, flag=1, file_path=file_path)
            else:
                sensitive_info = begin_info_extraction(
                    chunk_text, file_path=file_path)

            # 将发现的敏感信息添加到总列表中
            if sensitive_info:
                all_sensitive_info = all_sensitive_info + sensitive_info

        except Exception as e:
            logger.error(TAG + "sensitive_info_detect()-error: " + file_path)
            logger.error(e)
            # globalVar.set_error_list(file_path, e)

    # 在处理所有块之后，调用res_out.add_new_json
    if all_sensitive_info:
        res_out.add_new_json(file_path, all_sensitive_info)


def extract__config(file_path, namclean):
    res = ""
    content = read_file_content(file_path)
    res = begin_info_extraction(content, flag=1, file_path=file_path)
    res_out.add_new_json(file_path, res)


def extract__rule_based(file_path, namclean):
    res = ""
    content = read_file_content(file_path)
    res = begin_info_extraction(content, flag=2, file_path=file_path)
    res_out.add_new_json(file_path, res)


def extract__text(file_path, namclean):
    res = ""
    content = read_file_content(file_path)
    res = begin_info_extraction(content, flag=3, file_path=file_path)
    res_out.add_new_json(file_path, res)


def extract__pure_key_value(file_path, namclean):
    res = ""
    content = read_file_content(file_path)
    res = begin_info_extraction(content, flag=4, file_path=file_path)
    res_out.add_new_json(file_path, res)


def extract__code(file_path, namclean):
    res = ""
    content = read_file_content(file_path)
    res = begin_info_extraction(content, flag=5, file_path=file_path)
    res_out.add_new_json(file_path, res)


def read_file_content(file_path):
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        content = ""
    return content


######################### 常见文件 #################################################
# 常用文件提取操作, 如.txt...
def extract_universal(file_path, nameclean):
    logger.debug(TAG+"extract_universal(): " + file_path.split("/")[-1])
    text = universal_textract(file_path)
    sensitive_info_detect(file_path, text)


# 直接读取文件文本
def extract_direct_read(file_path, namclean):
    logger.debug(TAG+"extract_direct_read(): " + file_path.split("/")[-1])
    # 打开文件并读取其内容
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        pass
        logger.debug(TAG+"extract_direct_read()-erro: " + file_path)
        logger.debug(e)
        # globalVar.set_error_list(file_path, e)
    sensitive_info_detect(file_path, content)


# 配置文件读取和提取操作, 如.xml/.yml/.properties...
def extract_config(file_path, nameclean):
    logger.debug(TAG+"extract_config(): " + file_path.split("/")[-1])
    text = universal_file(file_path)
    sensitive_info_detect(file_path, text, flag=1)


# 图片文件ocr读取和提取操作, 如.jpg/.png...
def extract_pic(file_path, nameclean):
    logger.debug(TAG+"extract_pic(): " + file_path.split("/")[-1])

    pic_list = ocr_table_batch(file_path)

    # [# print(data) for data in pic_list[0][0:]]

    text_or_table_flag = is_png_text(pic_list[0])

    if text_or_table_flag:
        # is table
        pd_table_data = pd.DataFrame(pic_list[0][1:])
        # print(pd_table_data)
        res = single_table_sensitive_extraction(pd_table_data)
    else:
        # is pic
        # print(pic_list[0][1:])
        res = begin_info_extraction(pic_list[0], file_path=file_path)

    res_out.add_new_json(file_path, res)


# 判断图片识别结果（表格形式）还是文本
def is_png_text(info):
    if len(info) > 1:
        if len(info[1]) > 1:
            logger.debug(TAG + "is_png_text(): input is [table] png ")
            return True
    logger.debug(TAG + "is_png_text(): input is [text] png ")
    return False

######################### pdf file ###########################################


# .pdf文件读取和提取操作
def extract_pdf(file_path, nameclean):
    logger.debug(TAG+"extract_pdf(): " + file_path.split("/")[-1])
    text = pdf_file(file_path)
    sensitive_info_detect(file_path, text)


def extract_csv(file_path, nameclean):
    logger.debug(TAG+"extract_xlsx(): " + file_path.split("/")[-1])
    text = csv_file(file_path)
    res_out.add_new_json(file_path, text)


######################### office/wps file########################################
# (1).doc/.wps/docx
# (2).ppt/.dps/.pptx
# (3).xlsx/.et


# (1-1).doc文件读取和提取操作
def extract_doc(file_path, nameclean):
    logger.debug(TAG+"extract_doc(): " + file_path.split("/")[-1])
    text = docs_file(file_path, type=".doc")
    sensitive_info_detect(file_path, text)


# (1-2).wps文件读取和提取操作
def extract_wps(file_path, nameclean):
    logger.debug(TAG+"extract_wps(): " + file_path.split("/")[-1])

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
    logger.debug(TAG+"extract_docx(): " + file_path.split("/")[-1])
    text = docs_file(file_path, type=".docx")
    sensitive_info_detect(file_path, text)


# (2-1).ppt文件读取和提取操作
def extract_ppt(file_path, nameclean):
    logger.debug(TAG+"extract_ppt(): " + file_path.split("/")[-1])
    text = ppts_file(file_path, type=".ppt")
    sensitive_info_detect(file_path, text)


# (2-2).dps文件读取和提取操作
def extract_dps(file_path, nameclean):
    logger.debug(TAG+"extract_dps(): " + file_path.split("/")[-1])

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
    logger.debug(TAG+"extract_pptx(): " + file_path.split("/")[-1])
    text = ppts_file(file_path, type=".pptx")
    sensitive_info_detect(file_path, text)


# (3-1).xlsx文件读取和提取操作
def extract_xlsx(file_path, nameclean):
    logger.debug(TAG+"extract_xlsx(): " + file_path.split("/")[-1])
    text = xlsx_file(file_path)
    res_out.add_new_json(file_path, text)


# (3-2).et文件读取和提取操作
def extract_et(file_path, nameclean):
    logger.debug(TAG+"extract_et(): " + file_path.split("/")[-1])
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

######################### database file########################################
# .db 数据库文件的读取和提取操作
def extract_db(file_path, nameclean):
    logger.info(TAG+"extract_db(): " + file_path.split("/")[-1])
    text = db_file(file_path)
    res_out.add_new_json(file_path, text)

######################### code config file ################################

# token文件读取和提取操作
def is_token_file(file_path):

    if "token" in file_path:
        logger.debug(TAG+"is_token_file(): " + file_path)
        text = universal_file(file_path)
        res_out.add_new_json(file_path, text)
        return True

    return False


######################### code file########################################

# 源代码文件读取和提取操作
def extract_code_file(file_path, nameclean):
    logger.debug(TAG+"extract_code_file(): " + os.path.basename(file_path))
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
    logger.debug(TAG+"extract_eml(): " + file_path.split("/")[-1])
    eml_header, eml_text, attach_files_list = eml_file(file_path)

    sensitive_info = []
    sensitive_info_text = []
    if "text" in eml_text:
        sensitive_info_text = begin_info_extraction(eml_text["text"])

    if not len(sensitive_info_text) == 0:
        logger.debug(TAG+"extract_eml(): eml body has  sensitive infomation")
        sensitive_info.append(sensitive_info_text)

    if "table" in eml_text:
        logger.debug(TAG+"extract_eml(): eml body has table")
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
