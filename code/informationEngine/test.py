import re
from typing import Tuple

def item_protection(text: str) -> Tuple[str, dict]:
    placeholders = {}  # This dictionary will store placeholders and their corresponding content
    placeholders_counter = 1  # Counter for generating placeholders

    # Define regular expressions for different types of items you want to replace
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    jdbc_pattern = r'jdbc:mysql://[a-zA-Z0-9:/._-]+'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    ip_pattern = r'(?:\d{1,3}\.){3}\d{1,3}|localhost'

    port_pattern = r'\b(0|6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|[0-5]?[0-9]{1,4})\b'

    patterns = [email_pattern, jdbc_pattern, url_pattern, ip_pattern]

    for pattern in patterns:
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            # Replace only the first occurrence
            text = text.replace(item, placeholder, 1)
            placeholders_counter += 1

    return text, placeholders

text, placeholders = item_protection('''客户端使用手册(Windows)

为10.11.0.1''')

print(text)
print(placeholders)
