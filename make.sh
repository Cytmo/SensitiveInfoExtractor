# conda env python=3.8
# pip install --upgrade pip
# pip install python-pptx
# pip install textract
# sudo apt install build-essential


# install pic-ocr lib
#(1)
# sudo apt-get install tesseract-ocr
# pip install -i https://mirrors.aliyun.com/pypi/simple python-office -U
# pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
#(2)
# pip install paddleocr 
# wget https://www.openssl.org/source/openssl-1.1.1o.tar.gz
# tar -zxvf openssl-1.1.1o.tar.gz
# cd openssl-1.1.1o
# ./config
# make
# make test 
# sudo make install (on this moment you can't install python by pyenv)
# sudo find / -name libssl.so.1.1
# sudo ln -s /usr/local/lib/libssl.so.1.1  /usr/lib/libssl.so.1.1
# sudo find / -name libcrypto.so.1.1
# sudo ln -s /usr/local/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1
# pip uninstall opencv-python
# pip install opencv-python-headless

# pip install PyMuPDF     
# pip install eml_parser
# pip install beautifulsoup4
# pip install tabulate
# pip install spacy
# pip install aspose.slides
# sudo apt install libc6-dev 
# sudo apt install libgdiplus

# 具体见code/lib/readme.md
# pip install unrar  #直接pip install即可
# cd lib (code/lib)
# wget http://www.rarlab.com/rar/unrarsrc-5.4.5.tar.gz
# # tar -xzvf unrarsrc-5.4.5.tar.gz
# cd unrar
# sudo make lib
# sudo make install-lib

#Jhon安装
cd lib
wget https://www.openwall.com/john/k/john-1.9.0-jumbo-1.tar.gz
tar -xzvf john-1.9.0-jumbo-1.tar.gz

# # vim ~/.bashrc
# # export UNRAR_LIB_PATH=/usr/lib/libunrar.so

# pip install whispers

# 程序时间性能展示
# pip install snakeviz
# snakeviz ./log/profile_results.prof