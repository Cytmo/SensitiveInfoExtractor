# run main.py for 20 times
# write config to time_info.txt
echo "single process with image" >> time_info.txt
for i in {1..20}
do
    python main.py 
done

echo "multi-process with image" >> time_info.txt

for i in {1..20}
do
    python main.py -mp true
done

echo "single process without image" >> time_info.txt
for i in {1..20}
do
    python main.py -f ../data_no_image
done

echo "multi-process without image" >> time_info.txt
for i in {1..20}
do
    python main.py -f ../data_no_image -mp true
done