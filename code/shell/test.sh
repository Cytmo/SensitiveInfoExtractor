# cp -r ../data/ ../data_bak/
python3 main.py -f ../data_test
# open the newest log file
latest_log=$(ls -t log/ | head -n 1)
code "log/$latest_log"
# rm -r ../data/
# mv ../data_bak/ ../data/