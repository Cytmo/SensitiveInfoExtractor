# securityTextDetect825
## Requirements
`apt-get install antiword`

`apt-get install samdump2`

`pip install colorlog`

see more in `make.sh`
## Execute path
`security-text-detect-825/code`

## Tip

* install unrar

```
# pip install unrar  #直接pip install即可
# cd lib (code/lib)
# wget http://www.rarlab.com/rar/unrarsrc-5.4.5.tar.gz
# # tar -xzvf unrarsrc-5.4.5.tar.gz
# cd unrar
# sudo make lib
# sudo make install-lib

# # vim ~/.bashrc
# # export UNRAR_LIB_PATH=/usr/lib/libunrar.so
# 或者
# # vim ~/.zshrc
# # export UNRAR_LIB_PATH=/usr/lib/libunrar.so
# # source  ~/.zshrc

```