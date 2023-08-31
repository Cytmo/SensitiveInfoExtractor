import re
# 保存email地址 url ip地址等内容，防止被替换
def item_protection(text: str):
    placeholders = {}  # This dictionary will store placeholders and their corresponding content
    placeholders_counter = 1  # Counter for generating placeholders

    # Define regular expressions for different types of items you want to replace
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    patterns = [email_pattern, url_pattern, ip_pattern]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            item = match.group()
            placeholder = f'?{placeholders_counter}?'
            placeholders[placeholder] = item
            text = text.replace(item, placeholder, 1)  # Replace only the first occurrence
            placeholders_counter += 1

    return text, placeholders

# Example usage
input_text = "Contact us at john@example.com or visit http://example.com for more info. IP: 192.168.1.1"
processed_text, content_dict = item_protection(input_text)

print("Processed Text:", processed_text)
print("Content Dictionary:", content_dict)