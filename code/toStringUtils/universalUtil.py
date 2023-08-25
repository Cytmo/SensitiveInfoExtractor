import textract


# 使用texttract通用提取文件中文本信息
#  .csv, .doc, .docx, .eml, .epub, .gif, .htm, .html, .jpeg, .jpg, .json, .log, .mp3, .msg, .odt,
# .ogg, .pdf, .png, .pptx, .ps, .psv, .rtf, .tab, .tff, .tif, .tiff, .tsv, .txt, .wav, .xls, .xlsx
def universal_textract(file):
    text = textract.process(filename=file, encoding='utf-8')
    decoded_text = text.decode('utf-8')
    return decoded_text


# 直接读取,适用于可直接查看的文件
def universal_file(file):
    try:
        with open(file, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return str(e)
