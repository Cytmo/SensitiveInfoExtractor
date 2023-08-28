import textract

def read_ppt(path):
    text = textract.process(path)
    return text.decode("utf-8")

text = read_ppt('test/office/SSLVPNWindows.doc')
print(text)