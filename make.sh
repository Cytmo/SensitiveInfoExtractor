# 使用conda新建虚拟环境
conda create -n dev python=3.8
conda activate dev

# python库
pip install --upgrade pip
pip install python-pptx
pip install textract
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddleocr 
pip install opencv-python-headless
pip install PyMuPDF     
pip install eml_parser
pip install beautifulsoup4
pip install spacy
pip install aspose.slides
pip install unrar
pip install whispers
pip install snakeviz
pip install colorlog
pip install pygments    
pip install scikit-learn
pip install pyyaml
pip install aspose-words
pip install imbalanced-learn


# linux软件安装
sudo apt install antiword
sudo apt install build-essential
sudo apt install libc6-dev 
sudo apt install libgdiplus
sudo apt install samdump2
sudo apt-get install libopenblas-dev

# 依赖库配置
cd lib (code/lib)
wget http://www.rarlab.com/rar/unrarsrc-5.4.5.tar.gz
tar -xzvf unrarsrc-5.4.5.tar.gz
cd unrar
sudo make lib
sudo make install-lib

cd
wget https://www.openssl.org/source/openssl-1.1.1o.tar.gz
tar -zxvf openssl-1.1.1o.tar.gz
cd openssl-1.1.1o
./config
make
make test 
sudo make install
sudo ln -s /usr/local/lib/libssl.so.1.1  /usr/lib/libssl.so.1.1
sudo ln -s /usr/local/lib/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1
vim ~/.bashrc
export UNRAR_LIB_PATH=/usr/lib/libunrar.so


# 程序时间性能展示
#  snakeviz ./log/profile_results.prof