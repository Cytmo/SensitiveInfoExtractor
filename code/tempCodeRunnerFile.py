import json


reg_info = '''*disabled* Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
*disabled* Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
*disabled* :503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
*disabled* :504:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Zther0:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::'''
        # todo

lines = reg_info.strip().split('\n')
print(lines)
users = []

for line in lines:
    parts = line.split(':')
    print(parts)
    user_info = {
        "Status": "enabled",
        "Username": "None" if parts[0].strip() == "" else parts[0].strip(),
        "UserID": "None" if parts[1].strip() == "" else int(parts[1].strip()),
        "LMHash": "None" if parts[2].strip() == "" else parts[2].strip(),
        "NTLMHash": "None" if parts[3].strip() == "" else parts[3].strip(),
        "DomainName": "None" if parts[4].strip() == "" else parts[4].strip(),
        "GroupID": "None" if parts[5].strip() == "" else int(parts[5].strip()),
        "Description": "None" if parts[6].strip() == "" else parts[6].strip()
    }
    users.append(user_info)
    for user in users:
        if "*disabled*" in user["Username"]:
            user["Username"] = user["Username"].replace("*disabled*", "").strip()
            user["Status"] = "disabled"
            if user["Username"] == "":
                user["Username"] = "None"
        
reg_info_parsed =  json.dumps(users, indent=4)
print("reg_info_parsed is {}".format(reg_info_parsed)) 