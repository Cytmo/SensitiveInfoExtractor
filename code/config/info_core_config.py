import yaml
# This dictionary will store placeholders and their corresponding types
PLACEHOLDERS_CORRESPONDING_TYPE = {}
# 保存易混淆内容的位置 infomaion protection
ITEM_PROTECTION_DICT = {}
# 英文关键词列表
ENG_KEYWORDS_LIST = ["-u", "-p", "IP", "port", "-h",
                     "user", "password", "passw0rd", "address", "name", '\n']
# 英文替换词列表
ENG_REPLACEMENT_DICT = {"-p": "password", "port": "port", "-u": "user", "user": "user", "password": "password",
                        "-h": "address", "IP": "address", "address": "address", "name": "name", "passw0rd": "password"}
# 中文关键字列表
CHN_KEYWORDS_LIST = ["账号", "IP", "端口", "名称", "地址",
                     "姓名", "学号", "用户名", "密码", "密钥为", '\n']
# 中文替换列表
CHN_REPLACEMENT_DICT = {"账号": "user", "端口": "port", "名称": "user", "学号": "user", "用户名": "user",
                        "密钥为": "password", "密码": "password", "IP": "address", "地址": "address", "姓名": "name"}
# 信息提取列表
INFO_PATTERN = {"user": "user", "password": "password",
                "address": "address", "port": "port", "phonenumber": "phonenumber", "email": "email", "ip": "address", "url": "address"}

# TODO: 单项依赖, ID放后面
# 单项依赖信息组---前者需要后者存在
ONE_WAY_CONNECTED_INFO = {"port": "address",
                          "AWSMWSkey": "AWSMWSID",
                          "AWSAPIKey": "AWSAPIGateway",
                          "AWSS3Bucket": "AWSAccessKeyIDValue",
                          "GithubAppToken": "GitHub",
                          "GithubOAuthAccessToken": "GitHub",
                          "GithubPersonalAccessToken": "GitHub",
                          "GoogleAPIKey": "Google(GCP)ServiceAccount",
                          "GoogleOAuthAccessToken": "Google(GCP)ServiceAccount",
                          "SSH(DSA)privatekey": "SSH",
                          "SlackToken": "Slack",
                          "SlackUsertoken": "Slack",
                          "SlackUsertoken": "Slack",
                          "Slackaccesstoken": "Slackwebhook",
                          "SquareAPIKey": "Squareup",
                          "SquareOAuthSecret": "Squareup",
                          "Squareaccesstoken": "Squareup",
                          "StripeAPIKey": "Stripe",
                          "StripePublicLiveKey": "Stripe",
                          "TelegramBotAPIKey": "TelegramSecret",
                          "TwitterAccessToken": "TwitterSecretKey",
                          "TwitterOAuth": "TwitterClientID",
                          "awssecretkey": "awsaccesskeyid",
                          "facebook_oauth": "facebook_access_token",
                          "secretkey": "secretaccesskey",
                          "twitteroauthaccesssecret": "twitteroauthaccesstoken",
                          }

# 双向依赖信息组---等价关系，前后都需要存在才成立
TWO_WAY_CONNECTED_INFO = {"AWSsecretkey": "AWSaccesskey"}

# 信息提取替换词列表
REPLACED_KEYWORDS_LIST = ["{user}", "{password}",
                          "{address}", "{port}", "{phonenumber}", "{email}"]

# 代码提取词列表
SPECIAL_KEYWORDS_LIST = [
    "user",
    "pass",
    "address",
    "name",
    "port",
    "key",
    "auth",
    "salt",
    "host",
    "password",
    "username",
    "url",
    "driver",
]

CODE_FILE_EXTENSION = [
    '.java', '.py', '.go', '.js', '.php', '.c', '.cpp', '.cs', '.scala', '.html', '.css', '.xml', '.sh', '.bat', '.ps1', 'Dockerfile', '.h'
]
CONFIG_FILE_EXTENSION = [
    '.yml', '.yaml', '.json', '.toml', '.properties', '.ini'
]
IMAGE_FILE_EXTENSION = [
    '.jpg', '.png', '.bmp', '.jpeg', '.gif', '.svg'
]
# 读取YAML文件
with open('config/rules-stable.yml', 'r') as yaml_file:
    SENSITIVE_INFO_PATTERN = yaml.safe_load(yaml_file)
    for pattern in SENSITIVE_INFO_PATTERN['patterns']:
        name = pattern['pattern']['name'].strip()
        REPLACED_KEYWORDS_LIST.append("{"+name+"}")
