from pprint import pprint
from paddlenlp import Taskflow



text = open('test/text.txt', 'r').read()

# schema = ['用户名', '密码'] # Define the schema for entity extraction
# ie = Taskflow('information_extraction', schema=schema)
# pprint(ie(text)) # Better print results using pprint

from paddlenlp import Taskflow
schema = ['名称','地址','工号或学号', '密码']

# ie = Taskflow('information_extraction',
#                   schema=schema,
#                   schema_lang="ch",
#                   batch_size=16,
#                   model='uie-nano',
#                   position_prob=0.5,
#                   precision='fp32',
#                   use_fast=False)
# pprint(ie(text))

ner = Taskflow("ner")
pprint(ner(text))
