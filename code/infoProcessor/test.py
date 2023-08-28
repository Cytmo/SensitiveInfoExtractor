import paddlenlp
from paddlenlp import tag 

text = """Your text here"""

tokenizer = Tokenizer(paddlenlp.datasets.load_vocabulary('bert-base-chinese'))
tokens = tokenizer(list(text))

print("IP Addresses:")
for i in range(len(tokens)-3):
    if tokens[i].isdigit() and tokens[i+1] == '.' and tokens[i+2].isdigit() and tokens[i+3] == '.':
        print(''.join([tokens[i].text, tokens[i+1].text, tokens[i+2].text, tokens[i+3].text]))
        
print("\nUsernames:")
usernames = tag.ner(list(text), model='bert-base-chinese', return_tensor=False)
for entity in usernames:
    if entity[1] == 'PER':
        print(entity[0])
        
print("\nPasswords:")  
for i in range(len(tokens)-1):
    if tokens[i].text == '密码':
        print(tokens[i+1].text)