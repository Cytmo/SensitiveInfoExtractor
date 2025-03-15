# 安装指南

## 1. 环境准备

### 创建并激活conda虚拟环境
```bash
# 使用Python 3.8创建名为dev的虚拟环境
conda create -n dev python=3.8
# 激活环境
conda activate dev
```

## 2. 安装Python依赖

```bash
# 安装指定版本的pip
pip install pip==24.0

# 安装项目依赖
pip install -r requirements.txt

# 安装textract（不检查依赖）
pip install textract==1.6.5 --no-dependencies
```

## 3. 系统依赖安装

### 安装Linux软件包
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

## 4. 第三方库配置

### 安装unrar
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
```

### 安装OpenSSL
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

### 配置环境变量
```bash
# 编辑bashrc文件
echo 'export UNRAR_LIB_PATH=/usr/lib/libunrar.so' >> ~/.bashrc

# 使环境变量生效
source ~/.bashrc
```
