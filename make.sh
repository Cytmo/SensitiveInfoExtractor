# pip install --upgrade pip
# pip install python-pptx
# pip install unrar
cd maker_folder
# tar -xzvf unrarsrc-5.4.5.tar.gz
cd unrar
sudo make lib
sudo make install-lib

# vim ~/.bashrc
# export UNRAR_LIB_PATH=/usr/lib/libunrar.so