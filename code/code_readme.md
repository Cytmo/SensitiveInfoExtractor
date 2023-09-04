```
├── __init__.py
├── infoProcessor
├── lib
│   └── unrar
├── main.py
├── readme.md
├── tempCodeRunnerFile.py
├── toStringUtils
└── util
```

* unrar

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
