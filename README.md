# 安全文本检测系统

一个用于检测文档和图像中敏感信息的工具，支持多种文件格式和检测模式。

## 1. 系统环境要求

### 系统依赖
```bash
# 文档处理工具
sudo apt install antiword

# 开发工具
sudo apt install build-essential
sudo apt install libc6-dev

# 图形处理库
sudo apt install libgdiplus

# 其他工具
sudo apt install samdump2
sudo apt-get install libopenblas-dev
```

### Python环境
推荐使用Python 3.8
```bash
# 创建并激活conda虚拟环境
conda create -n dev python=3.8
conda activate dev

# 安装指定版本的pip
pip install pip==24.0

# 安装项目依赖
pip install -r requirements.txt

# 安装textract（不检查依赖）
pip install textract==1.6.5 --no-dependencies
```

### 第三方库配置

#### 安装unrar
```bash
# 创建目录
mkdir -p code/lib
cd code/lib

# 下载并解压unrar源码
wget http://www.rarlab.com/rar/unrarsrc-5.4.5.tar.gz
tar -xzvf unrarsrc-5.4.5.tar.gz

# 编译和安装
cd unrar
sudo make lib
sudo make install-lib

# 配置环境变量
echo 'export UNRAR_LIB_PATH=/usr/lib/libunrar.so' >> ~/.bashrc
source ~/.bashrc
```

#### 安装OpenSSL
```bash
# 创建目录
mkdir -p code/lib/openssl
cd code/lib/openssl

# 下载并解压OpenSSL源码
wget https://www.openssl.org/source/openssl-1.1.1o.tar.gz
tar -zxvf openssl-1.1.1o.tar.gz

# 编译和安装
cd openssl-1.1.1o
./config
make
make test 
sudo make install

# 创建符号链接
sudo ln -s /usr/local/lib/libssl.so.1.1 /usr/lib/libssl.so.1.1
sudo ln -s /usr/local/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1
```

## 2. 支持的文件类型

系统支持多种文件格式的敏感信息检测，包括：

### 文档文件
- Microsoft Office文档 (`.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`)
- PDF文档 (`.pdf`)
- 富文本格式 (`.rtf`)
- 文本文件 (`.txt`)
- 标记语言文件 (`.xml`, `.html`, `.json`)
- CSV文件 (`.csv`)

### 图像文件
- 常见图像格式 (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`)
- 图像中的嵌入文本将通过OCR技术进行识别和分析

### 归档和压缩文件
- 压缩文件 (`.zip`, `.rar`, `.7z`, `.tar`, `.gz`)
- 系统会自动解压并扫描内部文件

### 数据库文件
- MySQL (`.sql`, `.myd`, `.myi`, `.frm`, `.ibd`)
- PostgreSQL (`.sql`, `.dump`)
- SQL Server (`.mdf`, `.ldf`, `.bak`)
- SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Oracle (`.dmp`, `.dbf`)
- 通用SQL脚本 (`.sql`)

### 配置和日志文件
- 配置文件 (`.conf`, `.config`, `.ini`, `.properties`, `.env`)
- 日志文件 (`.log`)
- 系统文件 (`.bat`, `.sh`, `.yaml`, `.yml`)

### 代码文件
- 脚本语言 (`.py`, `.js`, `.php`, `.rb`, `.pl`)
- 编译语言 (`.c`, `.cpp`, `.h`, `.java`, `.cs`)
- Web前端 (`.html`, `.css`, `.jsx`, `.vue`)

### 其他格式
- 电子邮件 (`.eml`, `.msg`)
- CAD文件 (`.dwg`, `.dxf`)
- 电子书格式 (`.epub`, `.mobi`)

对于不同类型的文件，系统使用不同的处理策略：
- 文本类文件：直接进行正则表达式匹配和内容分析
- 二进制文件：先提取文本内容，再进行分析
- 图像文件：使用OCR技术识别图像中的文本内容
- 压缩文件：先解压，然后递归处理内部文件
- 数据库文件：提取SQL语句和数据库结构进行分析

## 3. 运行方式

### 命令行直接运行
执行路径应在项目代码目录下：
```bash
cd security-text-detect-825/code
python main.py -f ../data -t output/time_info.txt
```

### 交互式运行脚本

这个交互式脚本可以帮助您更方便地设置参数并运行安全文本检测程序。

#### 使用方法

1. 确保您在项目根目录下执行脚本：

```bash
python run_interactive.py
```

2. 脚本会首先提示您选择预定义的工作模式：

   - **全功能模式**：检测所有类型的敏感信息
   - **纯正则匹配模式**：仅使用正则表达式匹配，关闭认证信息搜索（默认）
   - **仅认证信息模式**：只检测用户名和密码信息
   - **全量输出模式**：输出所有匹配到的信息，包括无关联信息
   - **自定义模式**：手动设置所有参数

3. 根据您选择的模式，脚本会引导您设置必要的参数：

   - **扫描文件夹路径**：要扫描的文件夹，默认为"../data"
   - **是否使用多进程**：是否启用多进程处理，默认为"否"
   - **时间信息输出文件**：程序运行时间信息的输出位置，默认为"output/time_info.txt"
   - **是否处理非图片文件内部中的图片**：是否处理嵌入在非图片文件中的图片，默认为"否"
   - **是否清空workspace缓存目录**：程序结束后是否清理临时文件，默认为"是"
   - **是否输出无关联的敏感信息**：是否输出不满足关联规则的敏感信息，默认为"否"
   - **是否启用认证信息搜索模式**：是否搜索用户名和密码相关信息，默认为"是"

   注意：如果您选择了预定义模式（非"自定义模式"），部分参数将自动设置，您只需指定扫描文件夹和时间信息输出文件。

4. 在完成参数设置后，脚本会显示即将执行的完整命令，并询问您是否确认执行。

#### 预定义工作模式说明

| 模式名称 | 说明 | 特点 |
|---------|------|------|
| 全功能模式 | 检测所有类型的敏感信息 | 平衡检测效果和性能 |
| 纯正则匹配模式 | 仅使用正则表达式匹配敏感信息 | 默认配置，关闭认证信息搜索，直接输出正则匹配到的内容，不进行其他过滤 |
| 仅认证信息模式 | 只检测用户名和密码信息 | 专注于查找认证凭据，减少其他敏感信息的干扰 |
| 全量输出模式 | 输出所有匹配到的敏感信息 | 启用所有检测功能，并输出所有匹配项，包括无关联信息 |
| 自定义模式 | 手动设置所有参数 | 完全自定义程序行为，适合高级用户 |

#### 命令行参数说明

| 参数名称 | 命令行选项 | 默认值 | 说明 |
|---------|-----------|-------|------|
| 扫描文件夹 | -f, --folder | ../data | 要扫描的文件夹路径 |
| 多进程 | -mp, --multiprocess | false | 是否使用多进程执行 |
| 时间输出 | -t, --time | output/time_info.txt | 时间信息输出文件路径 |
| 处理图片 | -p, --picture | false | 是否处理非图片文件内部中的图片 |
| 清理工作区 | -c, --clean | true | 程序运行结束后是否清空workspace缓存目录 |
| 无关联敏感信息 | -ur, --unrelated | false | 是否输出不满足关联规则的敏感信息 |
| 认证信息搜索 | -auth, --auth_search | true | 是否搜索用户名和密码相关信息 |

## 4. 错误处理与注意事项

- 如果脚本无法找到code目录，会显示警告信息。
- 运行过程中出现任何错误都会被捕获并显示。
- 您可以随时按下Ctrl+C中断脚本执行。
- 确保您已经安装了所有必要的依赖项。
- 处理大型文件或大量文件时，可能需要增加系统资源限制。

## 5. 系统架构

### 文件处理流程
系统采用模块化设计，文件处理流程如下：
1. 扫描指定目录下的所有文件
2. 根据文件扩展名识别文件类型
3. 调用对应的处理模块提取文本内容
4. 使用敏感信息检测引擎分析文本并提取敏感信息
5. 生成检测报告

### 核心模块
- `main.py`：主程序入口，处理命令行参数和调度处理流程
- `toStringUtils/`：各种文件类型的文本提取工具
  - `databaseUtil.py`：数据库文件处理
  - `picUtil.py`：图像文件处理
  - `officeUtil.py`：Office文档处理
  - `configUtil.py`：配置文件处理
  - `universalUtil.py`：通用文件处理
- `informationEngine/`：敏感信息检测和分析引擎
  - `info_core.py`：核心检测逻辑
  - `table_extract.py`：表格数据处理和分析
- `util/`：工具类
  - `extractInfo.py`：文件提取和处理函数
  - `fileUtil.py`：文件操作工具
  - `spilitUtil.py`：文件分割处理

所有提取的内容都会通过敏感信息检测引擎进行分析，使用正则表达式和关键词匹配等技术识别敏感信息。