from datetime import datetime
import easyocr
from paddleocr import PaddleOCR
import textract
import os
# 日志模块
from util.logUtils import LoggerSingleton
TAG = "toStringUtils.picUtil.py-"
logger = LoggerSingleton().get_logger()

"""
picUtil: 图片OCR
* 主流OCR: https://www.jianshu.com/p/d19dba26f275
"""


# 1st OCR method: 使用textract中的ocr方式识别图片(tesseract-ocr)
# 效果: 表格截图中短文本识别效果较差且顺序错乱, 代码截图识别效果可以
def ocr_textract(file):
    text = textract.process(filename=file, encoding='utf-8')
    # 解码
    decoded_text = text.decode('utf-8')
    lines = decoded_text.strip().split("\n")
    # Optionally, you can convert each line to a list
    res = [item.strip() for item in lines if item.strip() != ""]
    return res


# 2nd OCR method: 使用百度PaddleOCR
# 效果: 识别率很高，但是耗时较长
def ocr_paddleocr(file):
    ocr = PaddleOCR(lang="ch",
                    use_gpu=False,
                    det_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
                    cls_model_dir="modes/ocr/paddleORC_model/ch_ppocr_mobile_v2.0_cls_infer/",
                    rec_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_rec_infer/")
    result = ocr.ocr(file)
    # 注：
    # result是一个list，每个item包含了文本框，文字和识别置信度
    # line的格式为：
    # [[[3.0, 149.0], [43.0, 149.0], [43.0, 163.0], [3.0, 163.0]], ('人心安', 0.6762619018554688)]
    # 文字框 boxes = line[0]，包含文字框的四个角的(x,y)坐标
    # 文字 txts = line[1][0]
    # 识别置信度 scores = line[1][1]
    res = []
    for line in result:
        for x in line:
            res.append(x[1][0])
    return res


# 3rd OCR method: 使用EasyOCR
# 效果：较为均衡，处于1th,2nd之间
def ocr_easyocr(file):
    reader = easyocr.Reader(['ch_sim', 'en'], False)  # False为不使用GPU
    # decoder 为引擎，detail 为是否显示位置信息 batch_size 设置越大，占用内存越高，识别速度越快
    result = reader.readtext(
        image=file, decoder='greedy', batch_size=20, detail=0)
    return result


def read_all_pic(folder_path, image_extensions=None):
    if image_extensions is None:
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    image_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(root, file))

    return image_paths


# 图片OCR识别
def pic_file(file):
    starttime = datetime.now()

    # 选择识别方式
    res = ocr_textract(file)
    # res = ocr_paddleocr(file)
    # res = ocr_easyocr(file)

    endtime = datetime.now()
    print('Speed time', (endtime-starttime).seconds, 's')
    return res


def ocr_batch_paddle(folder_path):
    image_paths = read_all_pic(folder_path)

    ocr = PaddleOCR(lang="ch",
                    use_gpu=False,
                    det_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_det_infer/",
                    cls_model_dir="modes/ocr/paddleORC_model/ch_ppocr_mobile_v2.0_cls_infer/",
                    rec_model_dir="modes/ocr/paddleORC_model/ch_ppocr_server_v2.0_rec_infer/")

    image_all_text = ""
    for image_path in image_paths:
        logger.info(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr.ocr(image_path)
        res = []
        for line in image_info:
            for x in line:
                res.append(x[1][0])

        if not len(res) == 0:
            image_string = "\n".join(res)
            image_all_text = image_all_text+"\n"+image_string
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is not none, str len is "+str(len(image_all_text)))
        # else:
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is none")
    return image_all_text


def ocr_batch_textract(folder_path):
    image_paths = read_all_pic(folder_path)

    image_all_text = ""
    for image_path in image_paths:
        logger.info(TAG+"ppt_and_dps_file(): "+image_path)
        image_info = ocr_textract(image_path)
        if not len(image_info) == 0:
            image_string = "\n".join(image_info)
            image_all_text = image_all_text+"\n"+image_string
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is not none, str len is "+str(len(image_all_text)))
        # else:
        #     logger.info(TAG+"ppt_and_dps_file(): handle " +
        #                 image_path + " is none")
    return image_all_text

# print(pic_file("data/HCC维护信息.png"))
# print(pic_file("data/carbon.jpg"))
