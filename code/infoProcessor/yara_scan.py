import yara

import yara
rule = yara.compile(source='rule foo: bar {strings: $a = "lmn" condition: $a}')
matches = rule.match(data='abcdefgjiklmnoprstuvwxyz')
print(matches)